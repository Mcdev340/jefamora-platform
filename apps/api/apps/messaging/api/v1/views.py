from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.api.v1.serializers import MessageSerializer
from apps.core.exceptions import APIError
from apps.core.permissions import IsEmailVerified
from apps.messaging.models import Conversation, Message
from apps.moderation.services import users_are_blocked
from apps.notifications.services import notify


def _conversation_for(user, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.select_related("booking__client__user", "booking__professional__user"),
        pk=conversation_id,
    )
    booking = conversation.booking
    participants = {booking.client.user_id, booking.professional.user_id}
    if user.id not in participants and user.role != "super_admin":
        raise APIError("forbidden", "Vous ne participez pas à cette mission.", status_code=403)
    if user.role != "super_admin" and users_are_blocked(booking.client.user_id, booking.professional.user_id):
        raise APIError("blocked", "La messagerie est indisponible pour ce contact.", status_code=403)
    return conversation


class MessageListCreateView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, conversation_id):
        conversation = _conversation_for(request.user, conversation_id)
        messages = conversation.messages.filter(is_hidden=False)
        return Response(MessageSerializer(messages, many=True).data)

    def post(self, request, conversation_id):
        conversation = _conversation_for(request.user, conversation_id)
        content = (request.data.get("content") or "").strip()
        if not content:
            raise APIError("validation_error", "Message vide.", fields={"content": ["Obligatoire."]})
        message = Message(conversation=conversation, sender=request.user, content=content)
        message.save()
        booking = conversation.booking
        recipient = booking.professional.user if request.user.id == booking.client.user_id else booking.client.user
        notify(
            recipient=recipient,
            kind="message_received",
            title="Nouveau message",
            body=content[:180],
            payload={"conversation_id": str(conversation.id)},
        )
        return Response(MessageSerializer(message).data, status=201)
