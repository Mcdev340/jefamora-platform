from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditLog
from apps.core.permissions import IsSuperAdmin


class AuditLogListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        logs = AuditLog.objects.select_related("actor").order_by("-created_at")[:100]
        return Response(
            [
                {
                    "id": str(item.id),
                    "action": item.action,
                    "actor": item.actor.email if item.actor_id else None,
                    "target_type": item.target_type,
                    "target_id": str(item.target_id) if item.target_id else None,
                    "created_at": item.created_at,
                }
                for item in logs
            ]
        )
