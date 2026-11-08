from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import audit
from apps.catalog.api.v1.serializers import PortfolioMediaSerializer, PortfolioSerializer
from apps.core.exceptions import APIError
from apps.core.files import resolve_private_file, store_private_file
from apps.core.permissions import IsEmailVerified, IsProfessional
from apps.portfolio.models import PortfolioItem, PortfolioMedia


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
        item = get_object_or_404(PortfolioItem, pk=item_id, profile=request.user.professional_profile)
        uploaded = request.FILES.get("file")
        if uploaded is None:
            raise APIError("validation_error", "Fichier manquant.", fields={"file": ["Obligatoire."]})
        key = store_private_file(uploaded, "portfolio")
        media = PortfolioMedia.objects.create(
            item=item,
            media_type=request.data.get("media_type", PortfolioMedia.MediaType.IMAGE),
            file_key=key,
            display_order=request.data.get("display_order") or 0,
        )
        return Response(PortfolioMediaSerializer(media).data, status=201)


class PortfolioMediaDownloadView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, media_id):
        media = get_object_or_404(PortfolioMedia.objects.select_related("item__profile__user"), pk=media_id)
        owner = media.item.profile.user_id == request.user.id
        published = media.item.status == PortfolioItem.Status.PUBLISHED
        if not owner and not published and request.user.role != "super_admin":
            raise APIError("forbidden", "Ce média n'est pas public.", status_code=403)
        return FileResponse(resolve_private_file(media.file_key).open("rb"), as_attachment=True)
