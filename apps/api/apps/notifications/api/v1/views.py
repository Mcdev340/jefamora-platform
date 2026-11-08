from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import APIError
from apps.core.permissions import IsEmailVerified
from apps.notifications.models import Notification


class NotificationListView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        notes = Notification.objects.filter(recipient=request.user)[:50]
        return Response(
            [
                {
                    "id": str(item.id),
                    "kind": item.kind,
                    "title": item.title,
                    "body": item.body,
                    "is_read": item.is_read,
                    "created_at": item.created_at,
                }
                for item in notes
            ]
        )


class NotificationReadView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request, notification_id):
        updated = Notification.objects.filter(recipient=request.user, pk=notification_id).update(is_read=True)
        if not updated:
            raise APIError("not_found", "Notification introuvable.", status_code=404)
        return Response(status=204)
