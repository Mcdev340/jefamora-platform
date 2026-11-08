from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsEmailVerified
from apps.privacy.models import DataDeletionRequest
from apps.privacy.services import grant_consent, request_deletion


class ConsentView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request):
        consent = grant_consent(
            user=request.user,
            code=request.data.get("code", "privacy"),
            granted=bool(request.data.get("granted", True)),
            version=request.data.get("version", "v1"),
        )
        return Response({"id": str(consent.id)}, status=201)


class DeletionView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        items = DataDeletionRequest.objects.filter(user=request.user)
        return Response(
            [{"id": str(item.id), "status": item.status, "created_at": item.created_at} for item in items]
        )

    def post(self, request):
        deletion = request_deletion(user=request.user, reason=request.data.get("reason", ""))
        return Response({"id": str(deletion.id), "status": deletion.status}, status=201)
