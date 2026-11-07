from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Endpoint public utilisé par les sondes de santé et Coolify."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "jefamora-api"})
