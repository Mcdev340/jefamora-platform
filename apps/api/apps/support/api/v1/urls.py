from django.urls import path

from apps.support.api.v1.views import DisputeEvidenceView, SupportTicketView

urlpatterns = [
    path("tickets/", SupportTicketView.as_view(), name="support-tickets"),
    path("disputes/<uuid:dispute_id>/evidence/", DisputeEvidenceView.as_view(), name="dispute-evidence"),
]
