from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.exceptions import APIError


class InactiveAssistantView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        raise APIError("module_inactive", "L'assistant sera activé après financement.", status_code=403)

    post = get
