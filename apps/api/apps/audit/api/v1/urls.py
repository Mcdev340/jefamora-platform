from django.urls import path

from apps.audit.api.v1.views import AuditLogListView

urlpatterns = [
    path("", AuditLogListView.as_view(), name="admin-audit"),
]
