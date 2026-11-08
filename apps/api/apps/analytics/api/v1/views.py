from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.selectors import platform_stats, record_export
from apps.core.permissions import IsSuperAdmin


class PlatformStatsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        return Response(platform_stats())


class AnalyticsExportView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        export = record_export(admin=request.user, export_type=request.data.get("export_type", "platform"))
        return Response({"id": str(export.id), "payload": export.payload}, status=201)
