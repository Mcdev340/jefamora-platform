from django.utils import timezone

from apps.audit.services import audit
from apps.bookings.models import Booking
from apps.core.exceptions import APIError
from apps.core.files import store_private_file
from apps.notifications.services import notify
from apps.support.models import Dispute, DisputeEvidence, SupportTicket

ACTIVE_BOOKING = {
    Booking.Status.CONFIRMED,
    Booking.Status.IN_PROGRESS,
    Booking.Status.COMPLETED_BY_PROFESSIONAL,
    Booking.Status.DISPUTED,
}


def _participant_ids(booking):
    return {booking.client.user_id, booking.professional.user_id}


def open_dispute(*, booking, user, description):
    if user.id not in _participant_ids(booking):
        raise APIError("forbidden", "Vous n'êtes pas partie à cette mission.", status_code=403)
    if booking.status not in ACTIVE_BOOKING:
        raise APIError("invalid_transition", "Un litige se ouvre sur une mission active.")
    if Dispute.objects.filter(booking=booking).exists():
        raise APIError("invalid_transition", "Un litige existe déjà pour cette mission.")
    dispute = Dispute.objects.create(booking=booking, opened_by=user, description=description)
    booking.status = Booking.Status.DISPUTED
    booking.save(update_fields=["status", "updated_at"])
    other = booking.professional.user if user.id == booking.client.user_id else booking.client.user
    notify(recipient=other, kind="dispute_opened", title="Litige ouvert", body=description[:180], payload={"dispute_id": str(dispute.id)})
    audit(actor=user, action="dispute.opened", target=dispute)
    return dispute


def add_evidence(*, dispute, user, uploaded):
    if user.id not in _participant_ids(dispute.booking) and user.role != "super_admin":
        raise APIError("forbidden", "Vous ne pouvez pas ajouter de preuve.", status_code=403)
    if dispute.status != Dispute.Status.OPEN:
        raise APIError("invalid_transition", "Ce litige est déjà tranché.")
    key = store_private_file(uploaded, "disputes")
    return DisputeEvidence.objects.create(
        dispute=dispute,
        uploaded_by=user,
        file_key=key,
        original_name=uploaded.name[:180],
    )


def resolve_dispute(*, dispute, admin, resolution, booking_status):
    if dispute.status != Dispute.Status.OPEN:
        raise APIError("invalid_transition", "Ce litige est déjà tranché.")
    allowed = {
        Booking.Status.CONFIRMED_BY_CLIENT,
        Booking.Status.CANCELLED,
        Booking.Status.DISPUTED,
    }
    if booking_status not in allowed:
        raise APIError("validation_error", "Statut final de réservation invalide.", fields={"booking_status": ["Invalide."]})
    dispute.status = Dispute.Status.RESOLVED
    dispute.resolution = resolution
    dispute.resolved_by = admin
    dispute.resolved_at = timezone.now()
    dispute.save()
    booking = dispute.booking
    booking.status = booking_status
    booking.save(update_fields=["status", "updated_at"])
    for person in (booking.client.user, booking.professional.user):
        notify(
            recipient=person,
            kind="dispute_resolved",
            title="Décision du litige",
            body=resolution,
            payload={"dispute_id": str(dispute.id)},
        )
    audit(actor=admin, action="dispute.resolved", target=dispute, metadata={"booking_status": booking_status})
    return dispute


def open_ticket(*, user, subject, description, priority):
    ticket = SupportTicket.objects.create(
        opened_by=user,
        subject=subject,
        description=description,
        priority=priority,
    )
    audit(actor=user, action="support.opened", target=ticket)
    return ticket


def close_ticket(*, ticket, admin):
    ticket.status = SupportTicket.Status.CLOSED
    ticket.save(update_fields=["status", "updated_at"])
    audit(actor=admin, action="support.closed", target=ticket)
    return ticket
