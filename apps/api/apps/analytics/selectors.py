from django.db.models import Count

from apps.analytics.models import AnalyticsExport
from apps.bookings.models import Booking
from apps.moderation.models import Report
from apps.professionals.models import ProfessionalProfile
from apps.service_requests.models import ServiceRequest
from apps.support.models import Dispute
from apps.verification.models import VerificationCase


def platform_stats():
    return {
        "professionals_verified": ProfessionalProfile.objects.filter(is_verified=True).count(),
        "verification_pending": VerificationCase.objects.filter(status=VerificationCase.Status.PENDING).count(),
        "open_requests": ServiceRequest.objects.filter(
            status__in=[ServiceRequest.Status.OPEN, ServiceRequest.Status.QUOTED]
        ).count(),
        "bookings": Booking.objects.count(),
        "open_disputes": Dispute.objects.filter(status=Dispute.Status.OPEN).count(),
        "open_reports": Report.objects.filter(status=Report.Status.OPEN).count(),
        "bookings_by_status": list(
            Booking.objects.values("status").annotate(total=Count("id")).order_by("status")
        ),
    }


def record_export(*, admin, export_type):
    payload = platform_stats()
    return AnalyticsExport.objects.create(
        requested_by=admin,
        export_type=export_type,
        payload=payload,
    )
