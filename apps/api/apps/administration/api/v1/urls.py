from django.urls import path

from apps.administration.api.v1.views import (
    AdminCatalogDetailView,
    AdminCatalogView,
    AdminDisputeDetailView,
    AdminDisputeListView,
    AdminDisputeResolveView,
    AdminModerationView,
    AdminReportCloseView,
    AdminReportDetailView,
    AdminReportListView,
    AdminTicketCloseView,
    AdminUserStateView,
    AdminVerificationDecisionView,
    AdminVerificationListView,
)

urlpatterns = [
    path("verification/", AdminVerificationListView.as_view(), name="admin-verification"),
    path(
        "verification/<uuid:case_id>/<str:decision>/",
        AdminVerificationDecisionView.as_view(),
        name="admin-verification-decision",
    ),
    path("reports/", AdminReportListView.as_view(), name="admin-reports"),
    path("reports/<uuid:report_id>/", AdminReportDetailView.as_view(), name="admin-report"),
    path("reports/<uuid:report_id>/close/", AdminReportCloseView.as_view(), name="admin-report-close"),
    path("moderation/", AdminModerationView.as_view(), name="admin-moderation"),
    path("users/<uuid:user_id>/suspend/", AdminUserStateView.as_view(), {"active": False}, name="admin-user-suspend"),
    path("users/<uuid:user_id>/reactivate/", AdminUserStateView.as_view(), {"active": True}, name="admin-user-reactivate"),
    path("disputes/", AdminDisputeListView.as_view(), name="admin-disputes"),
    path("disputes/<uuid:dispute_id>/", AdminDisputeDetailView.as_view(), name="admin-dispute"),
    path("disputes/<uuid:dispute_id>/resolve/", AdminDisputeResolveView.as_view(), name="admin-dispute-resolve"),
    path("support/tickets/", AdminTicketCloseView.as_view(), name="admin-tickets"),
    path("support/tickets/<uuid:ticket_id>/close/", AdminTicketCloseView.as_view(), name="admin-ticket-close"),
    path("catalog/<str:kind>/", AdminCatalogView.as_view(), name="admin-catalog"),
    path("catalog/<str:kind>/<uuid:pk>/", AdminCatalogDetailView.as_view(), name="admin-catalog-detail"),
]
