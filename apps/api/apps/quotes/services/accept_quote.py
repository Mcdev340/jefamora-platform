from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.bookings.models import Booking
from apps.quotes.models import Quote
from apps.service_requests.models import RequestRecipient, ServiceRequest


class QuoteDecisionError(Exception):
    """La demande ne peut pas accepter ce devis."""


@transaction.atomic
def accept_quote(*, quote, client_user):
    """Accepte un devis envoyé et ouvre la mission.

    Les autres devis de la même demande sont refusés. La réservation
    est créée depuis ce devis, et la conversation s'ouvre avec elle.
    """

    locked_request = (
        ServiceRequest.objects.select_for_update()
        .select_related("client")
        .get(pk=quote.service_request_id)
    )
    quote = (
        Quote.objects.select_for_update()
        .select_related("recipient")
        .get(pk=quote.pk, service_request=locked_request)
    )

    if locked_request.client.user_id != client_user.id:
        raise QuoteDecisionError("Seul le client de la demande peut accepter un devis.")
    if locked_request.status not in (
        ServiceRequest.Status.OPEN,
        ServiceRequest.Status.QUOTED,
    ):
        raise QuoteDecisionError("Cette demande n'accepte plus de devis.")
    if quote.recipient.service_request_id != locked_request.id:
        raise QuoteDecisionError("Ce devis ne correspond pas à la demande.")
    if quote.status != Quote.Status.SENT:
        raise QuoteDecisionError("Seul un devis envoyé peut être accepté.")
    if quote.expires_at is not None and quote.expires_at <= timezone.now():
        raise QuoteDecisionError("Ce devis est expiré.")
    if Booking.objects.filter(service_request=locked_request).exists():
        raise QuoteDecisionError("Cette demande a déjà une réservation.")

    quote.status = Quote.Status.ACCEPTED
    quote.save(update_fields=["status", "updated_at"])

    try:
        with transaction.atomic():
            booking = Booking.objects.create(
                quote=quote,
                scheduled_at=locked_request.desired_date,
            )
    except IntegrityError as exc:
        raise QuoteDecisionError("Cette demande a déjà une réservation.") from exc

    Quote.objects.filter(service_request=locked_request).exclude(pk=quote.pk).exclude(
        status__in=[Quote.Status.REFUSED, Quote.Status.EXPIRED]
    ).update(status=Quote.Status.REFUSED, updated_at=timezone.now())

    RequestRecipient.objects.filter(pk=quote.recipient_id).update(
        status=RequestRecipient.Status.ACCEPTED,
        updated_at=timezone.now(),
    )
    RequestRecipient.objects.filter(service_request=locked_request).exclude(
        pk=quote.recipient_id
    ).update(status=RequestRecipient.Status.REFUSED, updated_at=timezone.now())

    locked_request.status = ServiceRequest.Status.BOOKED
    locked_request.save(update_fields=["status", "updated_at"])
    return booking
