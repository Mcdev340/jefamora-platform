from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clients.models import ClientProfile
from apps.core.exceptions import APIError
from apps.core.permissions import IsClient


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ("id", "company_name")
        read_only_fields = ("id",)


class ClientProfileView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        return Response(ClientProfileSerializer(request.user.client_profile).data)

    def patch(self, request):
        profile = request.user.client_profile
        serializer = ClientProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data:
            raise APIError("validation_error", "Aucune modification envoyée.")
        serializer.save()
        return Response(serializer.data)
