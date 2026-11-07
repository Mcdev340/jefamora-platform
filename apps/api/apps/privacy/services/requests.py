from django.db.models import Q

from apps.audit.services import audit
from apps.bookings.models import Booking
from apps.core.exceptions import APIError
from apps.privacy.models import DataDeletionRequest, UserConsent
from apps.support.models import Dispute


def grant_consent(*, user, code, granted, version="v1"):
    return UserConsent.objects.create(user=user, code=code, granted=granted, version=version)


def request_deletion(*, user, reason=""):
    open_dispute = Dispute.objects.filter(
        Q(booking__client__user=user) | Q(booking__professional__user=user),
        status=Dispute.Status.OPEN,
    ).exists()
    active_mission = Booking.objects.filter(
        Q(client__user=user) | Q(professional__user=user),
        status__in=[
            Booking.Status.CONFIRMED,
            Booking.Status.IN_PROGRESS,
            Booking.Status.COMPLETED_BY_PROFESSIONAL,
            Booking.Status.DISPUTED,
        ],
    ).exists()
    if open_dispute or active_mission:
        deletion = DataDeletionRequest.objects.create(
            user=user,
            reason=reason,
            status=DataDeletionRequest.Status.BLOCKED,
        )
        audit(actor=user, action="privacy.deletion_blocked", target=deletion)
        raise APIError(
            "deletion_blocked",
            "Une mission ou un litige est encore ouvert. La suppression attendra sa clôture.",
            status_code=409,
        )
    user.is_active = False
    user.save(update_fields=["is_active", "updated_at"])
    deletion = DataDeletionRequest.objects.create(
        user=user,
        reason=reason,
        status=DataDeletionRequest.Status.PENDING,
    )
    audit(actor=user, action="privacy.deletion_requested", target=deletion)
    return deletion
