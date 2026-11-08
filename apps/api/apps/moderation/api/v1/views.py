from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsEmailVerified
from apps.moderation.models import Report
from apps.moderation.services import block_user, file_report, unblock_user


class ReportView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request):
        report = file_report(
            reporter=request.user,
            target_type=request.data.get("target_type"),
            target_id=request.data.get("target_id"),
            reason=request.data.get("reason", Report.Reason.OTHER),
            description=request.data.get("description", ""),
        )
        return Response({"id": str(report.id), "status": report.status}, status=201)


class BlockView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request):
        block = block_user(blocker=request.user, blocked_id=request.data["user"])
        return Response({"id": str(block.id)}, status=201)

    def delete(self, request):
        unblock_user(blocker=request.user, blocked_id=request.data["user"])
        return Response(status=204)
