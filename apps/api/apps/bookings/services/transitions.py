from django.db import transaction
from django.utils import timezone

from apps.audit.services import audit
from apps.bookings.models import Booking
from apps.core.exceptions import APIError
from apps.notifications.services import notify


def _professional_booking(booking_id, user):
    booking = Booking.objects.select_related("professional__user", "client__user").get(pk=booking_id)
    if booking.professional.user_id != user.id:
        raise APIError("forbidden", "Cette mission ne vous appartient pas.", status_code=403)
    return booking


def _client_booking(booking_id, user):
    booking = Booking.objects.select_related("professional__user", "client__user").get(pk=booking_id)
    if booking.client.user_id != user.id:
        raise APIError("forbidden", "Cette mission ne vous appartient pas.", status_code=403)
    return booking


@transaction.atomic
def start_booking(*, booking_id, user):
    booking = _professional_booking(booking_id, user)
    if booking.status != Booking.Status.CONFIRMED:
        raise APIError("invalid_transition", "La mission ne peut pas être démarrée.")
    booking.status = Booking.Status.IN_PROGRESS
    booking.save(update_fields=["status", "updated_at"])
    notify(
        recipient=booking.client.user,
        kind="booking_started",
        title="Mission démarrée",
        body="Le professionnel a démarré la mission.",
        payload={"booking_id": str(booking.id)},
    )
    audit(actor=user, action="booking.started", target=booking)
    return booking


@transaction.atomic
def request_completion(*, booking_id, user):
    booking = _professional_booking(booking_id, user)
    if booking.status != Booking.Status.IN_PROGRESS:
        raise APIError("invalid_transition", "La mission doit être en cours.")
    booking.status = Booking.Status.COMPLETED_BY_PROFESSIONAL
    booking.completed_at = timezone.now()
    booking.save(update_fields=["status", "completed_at", "updated_at"])
    notify(
        recipient=booking.client.user,
        kind="booking_completion_requested",
        title="Confirmez la fin de mission",
        body="Le professionnel déclare la prestation terminée.",
        payload={"booking_id": str(booking.id)},
    )
    audit(actor=user, action="booking.completion_requested", target=booking)
    return booking


@transaction.atomic
def confirm_completion(*, booking_id, user):
    booking = _client_booking(booking_id, user)
    if booking.status != Booking.Status.COMPLETED_BY_PROFESSIONAL:
        raise APIError("invalid_transition", "Le professionnel n'a pas encore déclaré la fin.")
    booking.status = Booking.Status.CONFIRMED_BY_CLIENT
    booking.save(update_fields=["status", "updated_at"])
    notify(
        recipient=booking.professional.user,
        kind="booking_confirmed",
        title="Mission confirmée",
        body="Le client a confirmé la fin de la mission.",
        payload={"booking_id": str(booking.id)},
    )
    audit(actor=user, action="booking.confirmed", target=booking)
    return booking


def visible_bookings(user):
    queryset = Booking.objects.select_related(
        "client__user",
        "professional",
        "service_request",
        "quote",
    )
    if user.role == "client":
        return queryset.filter(client__user=user)
    if user.role == "professional":
        return queryset.filter(professional__user=user)
    if user.role == "super_admin":
        return queryset
    return queryset.none()
