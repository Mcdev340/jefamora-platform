from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.api.v1.serializers import (
    AvailabilitySerializer,
    ProfessionalCardSerializer,
    ProfessionalDetailSerializer,
    ServiceSerializer,
    ZoneSerializer,
)
from apps.core.exceptions import APIError
from apps.core.permissions import IsEmailVerified, IsProfessional
from apps.professionals.models import Availability, ProfessionalService
from apps.professionals.selectors import public_profile, search_professionals


def _uuid_param(value):
    if not value:
        return None
    return value


class ProfessionalListView(generics.ListAPIView):
    permission_classes = [IsEmailVerified]
    serializer_class = ProfessionalCardSerializer

    def get_queryset(self):
        params = self.request.query_params
        rating = params.get("min_rating")
        weekday = params.get("weekday")
        return search_professionals(
            trade=_uuid_param(params.get("trade")),
            specialty=_uuid_param(params.get("specialty")),
            zone=_uuid_param(params.get("zone")),
            min_rating=rating or None,
            weekday=int(weekday) if weekday not in (None, "") else None,
        )


class ProfessionalDetailView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, profile_id):
        profile = public_profile(profile_id)
        if profile is None:
            raise APIError("not_found", "Professionnel introuvable.", status_code=404)
        return Response(ProfessionalDetailSerializer(profile).data)


class OwnProfileView(APIView):
    permission_classes = [IsProfessional]

    def get(self, request):
        return Response(ProfessionalDetailSerializer(request.user.professional_profile).data)

    def patch(self, request):
        profile = request.user.professional_profile
        for field in ("business_name", "biography", "years_of_experience"):
            if field in request.data:
                setattr(profile, field, request.data[field])
        profile.save()
        return Response(ProfessionalDetailSerializer(profile).data)


class OwnZoneView(APIView):
    permission_classes = [IsProfessional]

    def put(self, request):
        profile = request.user.professional_profile
        zones = request.data.get("zone_ids", [])
        from apps.locations.models import Zone

        selected = list(Zone.objects.filter(pk__in=zones))
        if len(selected) != len(set(zones)):
            raise APIError("validation_error", "Une ou plusieurs zones sont inconnues.", fields={"zone_ids": ["Invalide."]})
        profile.assign_zones(selected)
        return Response(ZoneSerializer(profile.zones.all(), many=True).data)


class ServiceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsProfessional]
    serializer_class = ServiceSerializer

    def get_queryset(self):
        return ProfessionalService.objects.filter(profile=self.request.user.professional_profile)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.professional_profile)


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsProfessional]
    serializer_class = ServiceSerializer

    def get_queryset(self):
        return ProfessionalService.objects.filter(profile=self.request.user.professional_profile)


class AvailabilityListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsProfessional]
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        return Availability.objects.filter(profile=self.request.user.professional_profile)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.professional_profile)


class AvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsProfessional]
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        return Availability.objects.filter(profile=self.request.user.professional_profile)
