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

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.audit.services import audit
from apps.core.exceptions import APIError
from apps.notifications.services import notify
from apps.professionals.models import ProfessionalProfile
from apps.quotes.models import Quote, QuoteLine
from apps.service_requests.models import RequestRecipient, ServiceRequest


def _line_total(lines):
    total = Decimal("0")
    for line in lines:
        total += Decimal(line["quantity"]) * Decimal(line["unit_price"])
    return total.quantize(Decimal("1"))


@transaction.atomic
def send_quote(*, professional_user, service_request_id, total_amount, estimated_delay="", conditions="", expires_at=None, lines=None):
    try:
        profile = professional_user.professional_profile
    except ProfessionalProfile.DoesNotExist as exc:
        raise APIError("forbidden", "Profil professionnel introuvable.", status_code=403) from exc
    try:
        recipient = (
            RequestRecipient.objects.select_for_update()
            .select_related("service_request__client__user")
            .get(service_request_id=service_request_id, professional=profile)
        )
    except RequestRecipient.DoesNotExist as exc:
        raise APIError("forbidden", "Cette demande ne vous est pas adressée.", status_code=403) from exc
    service_request = recipient.service_request
    if recipient.status == RequestRecipient.Status.REFUSED:
        raise APIError("invalid_transition", "Vous avez déjà refusé cette demande.")
    if service_request.status not in (ServiceRequest.Status.OPEN, ServiceRequest.Status.QUOTED):
        raise APIError("invalid_transition", "Cette demande n'accepte plus de devis.")
    if lines:
        computed = _line_total(lines)
        if Decimal(total_amount) != computed:
            raise APIError(
                "validation_error",
                "Le montant total doit être la somme des lignes.",
                fields={"total_amount": [f"Attendu : {computed} F CFA."]},
            )
    quote = Quote(
        recipient=recipient,
        total_amount=total_amount,
        estimated_delay=estimated_delay,
        conditions=conditions,
        expires_at=expires_at,
        status=Quote.Status.SENT,
    )
    quote.save()
    for line in lines or []:
        QuoteLine.objects.create(
            quote=quote,
            label=line["label"],
            quantity=line["quantity"],
            unit_price=line["unit_price"],
        )
    recipient.status = RequestRecipient.Status.QUOTED
    recipient.save(update_fields=["status", "updated_at"])
    if service_request.status == ServiceRequest.Status.OPEN:
        service_request.status = ServiceRequest.Status.QUOTED
        service_request.save(update_fields=["status", "updated_at"])
    notify(
        recipient=service_request.client.user,
        kind="quote_received",
        title="Nouveau devis",
        body=f"{profile.business_name} vous a envoyé un devis.",
        payload={"quote_id": str(quote.id), "service_request_id": str(service_request.id)},
    )
    audit(actor=professional_user, action="quote.sent", target=quote)
    return quote


@transaction.atomic
def reject_quote(*, quote, client_user):
    quote = Quote.objects.select_for_update().select_related("service_request__client").get(pk=quote.pk)
    if quote.service_request.client.user_id != client_user.id:
        raise APIError("forbidden", "Vous ne pouvez pas refuser ce devis.", status_code=403)
    if quote.status != Quote.Status.SENT:
        raise APIError("invalid_transition", "Seul un devis envoyé peut être refusé.")
    if quote.expires_at and quote.expires_at <= timezone.now():
        quote.status = Quote.Status.EXPIRED
        quote.save(update_fields=["status", "updated_at"])
        raise APIError("invalid_transition", "Ce devis est expiré.")
    quote.status = Quote.Status.REFUSED
    quote.save(update_fields=["status", "updated_at"])
    service_request = quote.service_request
    still_open = Quote.objects.filter(
        service_request=service_request,
        status=Quote.Status.SENT,
    ).exists()
    if not still_open and service_request.status == ServiceRequest.Status.QUOTED:
        service_request.status = ServiceRequest.Status.OPEN
        service_request.save(update_fields=["status", "updated_at"])
    notify(
        recipient=quote.recipient.professional.user,
        kind="quote_refused",
        title="Devis refusé",
        body="Le client a refusé votre devis.",
        payload={"quote_id": str(quote.id)},
    )
    audit(actor=client_user, action="quote.refused", target=quote)
    return quote
