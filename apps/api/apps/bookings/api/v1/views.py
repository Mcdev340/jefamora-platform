from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.api.v1.serializers import BookingSerializer, MessageSerializer, ReviewReplySerializer, ReviewSerializer
from apps.bookings.services.transitions import (
    confirm_completion,
    request_completion,
    start_booking,
    visible_bookings,
)
from apps.conversations.models import Conversation, Message
from apps.core.exceptions import APIError
from apps.core.pagination import DefaultPagination
from apps.core.permissions import IsClient, IsEmailVerified, IsProfessional
from apps.moderation.services.actions import users_are_blocked
from apps.notifications.services import notify
from apps.reviews.models import Review
from apps.support.models import Dispute
from apps.support.services.cases import add_evidence, open_dispute


class BookingListView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(visible_bookings(request.user), request)
        return paginator.get_paginated_response(BookingSerializer(page, many=True).data)


class BookingDetailView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, booking_id):
        booking = get_object_or_404(visible_bookings(request.user), pk=booking_id)
        return Response(BookingSerializer(booking).data)


class BookingStartView(APIView):
    permission_classes = [IsProfessional]

    def post(self, request, booking_id):
        booking = start_booking(booking_id=booking_id, user=request.user)
        return Response(BookingSerializer(booking).data)


class BookingRequestCompletionView(APIView):
    permission_classes = [IsProfessional]

    def post(self, request, booking_id):
        booking = request_completion(booking_id=booking_id, user=request.user)
        return Response(BookingSerializer(booking).data)


class BookingConfirmCompletionView(APIView):
    permission_classes = [IsClient]

    def post(self, request, booking_id):
        booking = confirm_completion(booking_id=booking_id, user=request.user)
        return Response(BookingSerializer(booking).data)


class BookingDisputeView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request, booking_id):
        booking = get_object_or_404(visible_bookings(request.user).select_related("client__user", "professional__user"), pk=booking_id)
        dispute = open_dispute(booking=booking, user=request.user, description=request.data.get("description", ""))
        return Response({"id": str(dispute.id), "status": dispute.status}, status=201)


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


class ReviewCreateView(APIView):
    permission_classes = [IsClient]

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.validated_data["booking"]
        if booking.client.user_id != request.user.id:
            raise APIError("forbidden", "Vous ne pouvez noter que votre mission.", status_code=403)
        review = Review(
            booking_id=serializer.validated_data["booking"].id,
            rating=serializer.validated_data["rating"],
            comment=serializer.validated_data.get("comment", ""),
        )
        review.save()
        notify(
            recipient=review.booking.professional.user,
            kind="review_received",
            title="Nouvel avis",
            body=review.comment[:180],
            payload={"review_id": str(review.id)},
        )
        return Response(ReviewSerializer(review).data, status=201)


class ReviewDetailView(APIView):
    permission_classes = [IsEmailVerified]

    def patch(self, request, review_id):
        review = get_object_or_404(Review.objects.select_related("booking__client__user", "booking__professional__user"), pk=review_id)
        if request.user.id == review.booking.client.user_id:
            if "rating" in request.data:
                review.rating = request.data["rating"]
            if "comment" in request.data:
                review.comment = request.data["comment"]
        elif request.user.id == review.booking.professional.user_id:
            reply = ReviewReplySerializer(data=request.data)
            reply.is_valid(raise_exception=True)
            review.professional_reply = reply.validated_data["professional_reply"]
        else:
            raise APIError("forbidden", "Vous ne pouvez pas modifier cet avis.", status_code=403)
        review.save()
        return Response(ReviewSerializer(review).data)


class DisputeEvidenceView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request, dispute_id):
        dispute = get_object_or_404(Dispute.objects.select_related("booking__client", "booking__professional"), pk=dispute_id)
        uploaded = request.FILES.get("file")
        if uploaded is None:
            raise APIError("validation_error", "Fichier manquant.", fields={"file": ["Obligatoire."]})
        evidence = add_evidence(dispute=dispute, user=request.user, uploaded=uploaded)
        return Response({"id": str(evidence.id), "file_key": evidence.file_key}, status=201)
