from django.db.models import Q

from apps.professionals.models import ProfessionalProfile


def search_professionals(*, trade=None, specialty=None, zone=None, min_rating=None, weekday=None):
    queryset = (
        ProfessionalProfile.objects.filter(
            is_verified=True,
            user__is_active=True,
            verification_status=ProfessionalProfile.VerificationStatus.APPROVED,
        )
        .select_related("user")
        .prefetch_related("zones", "services__trade", "availabilities")
    )
    if trade:
        queryset = queryset.filter(services__trade_id=trade, services__is_active=True)
    if specialty:
        queryset = queryset.filter(services__specialty_id=specialty, services__is_active=True)
    if zone:
        queryset = queryset.filter(zones__id=zone, zones__is_active=True)
    if min_rating is not None:
        queryset = queryset.filter(average_rating__gte=min_rating)
    if weekday is not None:
        queryset = queryset.filter(availabilities__weekday=weekday, availabilities__is_available=True)
    return queryset.distinct()


def public_profile(profile_id):
    return (
        ProfessionalProfile.objects.filter(
            pk=profile_id,
            is_verified=True,
            user__is_active=True,
        )
        .select_related("user")
        .prefetch_related(
            "zones",
            "services__trade",
            "services__specialty",
            "availabilities",
            "portfolio_items__media",
            "bookings__review",
        )
        .filter(Q(verification_status=ProfessionalProfile.VerificationStatus.APPROVED))
        .first()
    )
