from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.api.v1.serializers import (
    AvailabilitySerializer,
    PortfolioSerializer,
    ProfessionalCardSerializer,
    ProfessionalDetailSerializer,
    ServiceSerializer,
    ZoneSerializer,
)
from apps.audit.services import audit
from apps.core.exceptions import APIError
from apps.core.files import resolve_private_file
from apps.core.permissions import IsEmailVerified, IsProfessional
from apps.portfolio.models import PortfolioItem, PortfolioMedia
from apps.professionals.models import Availability, ProfessionalService
from apps.search.selectors import public_profile, search_professionals


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


class PortfolioListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsProfessional]
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        return PortfolioItem.objects.filter(profile=self.request.user.professional_profile).prefetch_related("media")

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.professional_profile)


class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsProfessional]
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        return PortfolioItem.objects.filter(profile=self.request.user.professional_profile)


class PortfolioPublishView(APIView):
    permission_classes = [IsProfessional]

    def post(self, request, item_id):
        item = get_object_or_404(
            PortfolioItem.objects.prefetch_related("media"),
            pk=item_id,
            profile=request.user.professional_profile,
        )
        if item.status == PortfolioItem.Status.REJECTED:
            raise APIError("invalid_transition", "Cette réalisation a été refusée.")
        if not item.media.exists():
            raise APIError("validation_error", "Ajoutez au moins une photo avant de publier.")
        item.status = PortfolioItem.Status.PUBLISHED
        item.save(update_fields=["status", "updated_at"])
        audit(actor=request.user, action="portfolio.published", target=item)
        return Response(PortfolioSerializer(item).data)


class PortfolioMediaCreateView(APIView):
    permission_classes = [IsProfessional]

    def post(self, request, item_id):
        item = get_object_or_404(
            PortfolioItem,
            pk=item_id,
            profile=request.user.professional_profile,
        )
        uploaded = request.FILES.get("file")
        if uploaded is None:
            raise APIError("validation_error", "Fichier manquant.", fields={"file": ["Obligatoire."]})
        from apps.core.files import store_private_file

        key = store_private_file(uploaded, "portfolio")
        media = PortfolioMedia.objects.create(
            item=item,
            media_type=request.data.get("media_type", PortfolioMedia.MediaType.IMAGE),
            file_key=key,
            display_order=request.data.get("display_order") or 0,
        )
        from apps.catalog.api.v1.serializers import PortfolioMediaSerializer

        return Response(PortfolioMediaSerializer(media).data, status=201)


class PortfolioMediaDownloadView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, media_id):
        media = get_object_or_404(
            PortfolioMedia.objects.select_related("item__profile__user"),
            pk=media_id,
        )
        owner = media.item.profile.user_id == request.user.id
        published = media.item.status == PortfolioItem.Status.PUBLISHED
        if not owner and not published and request.user.role != "super_admin":
            raise APIError("forbidden", "Ce média n'est pas public.", status_code=403)
        return FileResponse(resolve_private_file(media.file_key).open("rb"), as_attachment=True)
