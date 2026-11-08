from django.urls import path

from apps.analytics.api.v1.views import AnalyticsExportView, PlatformStatsView

urlpatterns = [
    path("stats/", PlatformStatsView.as_view(), name="admin-stats"),
    path("exports/", AnalyticsExportView.as_view(), name="admin-exports"),
]
