from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import audit
from apps.core.permissions import IsClient, IsProfessional
from apps.notifications.services import notify
from apps.quotes.models import Quote
from apps.quotes.services import accept_quote, reject_quote, send_quote
from apps.service_requests.api.v1.serializers import QuoteCreateSerializer, QuoteSerializer


class QuoteCreateView(APIView):
    permission_classes = [IsProfessional]
    serializer_class = QuoteCreateSerializer

    def post(self, request):
        serializer = QuoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        quote = send_quote(
            professional_user=request.user,
            service_request_id=data["service_request"],
            total_amount=data["total_amount"],
            estimated_delay=data.get("estimated_delay", ""),
            conditions=data.get("conditions", ""),
            expires_at=data.get("expires_at"),
            lines=data.get("lines"),
        )
        return Response(QuoteSerializer(quote).data, status=201)


class QuoteRejectView(APIView):
    permission_classes = [IsClient]

    def post(self, request, quote_id):
        quote = get_object_or_404(Quote, pk=quote_id)
        rejected = reject_quote(quote=quote, client_user=request.user)
        return Response(QuoteSerializer(rejected).data)


class QuoteAcceptView(APIView):
    permission_classes = [IsClient]

    def post(self, request, quote_id):
        quote = get_object_or_404(Quote.objects.select_related("recipient__professional__user"), pk=quote_id)
        booking = accept_quote(quote=quote, client_user=request.user)
        notify(
            recipient=booking.professional.user,
            kind="quote_accepted",
            title="Devis accepté",
            body="Le client a confirmé la réservation.",
            payload={"booking_id": str(booking.id)},
        )
        audit(actor=request.user, action="quote.accepted", target=booking)
        from apps.bookings.api.v1.serializers import BookingSerializer

        return Response(BookingSerializer(booking).data, status=201)
