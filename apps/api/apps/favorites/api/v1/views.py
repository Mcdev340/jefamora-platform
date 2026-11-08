from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsClient
from apps.favorites.models import Favorite
from apps.professionals.models import ProfessionalProfile


class FavoriteView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        favorites = Favorite.objects.filter(client=request.user.client_profile).select_related("professional")
        return Response(
            [
                {
                    "id": str(item.id),
                    "professional": str(item.professional_id),
                    "name": item.professional.business_name,
                }
                for item in favorites
            ]
        )

    def post(self, request):
        professional = get_object_or_404(ProfessionalProfile, pk=request.data.get("professional"))
        favorite, _created = Favorite.objects.get_or_create(
            client=request.user.client_profile,
            professional=professional,
        )
        return Response({"id": str(favorite.id)}, status=201)

    def delete(self, request):
        Favorite.objects.filter(
            client=request.user.client_profile,
            professional_id=request.data.get("professional"),
        ).delete()
        return Response(status=204)
