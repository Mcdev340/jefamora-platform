from django.urls import path

from apps.moderation.api.v1.views import BlockView, ReportView

urlpatterns = [
    path("reports/", ReportView.as_view(), name="reports"),
    path("blocks/", BlockView.as_view(), name="blocks"),
]
