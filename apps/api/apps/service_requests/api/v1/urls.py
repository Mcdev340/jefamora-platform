from django.urls import path

from apps.service_requests.api.v1.views import (
    ServiceRequestAttachmentView,
    ServiceRequestCancelView,
    ServiceRequestDeclineView,
    ServiceRequestDetailView,
    ServiceRequestListCreateView,
    ServiceRequestQuoteListView,
)

urlpatterns = [
    path("", ServiceRequestListCreateView.as_view(), name="service-requests"),
    path("<uuid:request_id>/", ServiceRequestDetailView.as_view(), name="service-request"),
    path("<uuid:request_id>/cancel/", ServiceRequestCancelView.as_view(), name="service-request-cancel"),
    path("<uuid:request_id>/decline/", ServiceRequestDeclineView.as_view(), name="service-request-decline"),
    path("<uuid:request_id>/attachments/", ServiceRequestAttachmentView.as_view(), name="service-request-attachment"),
    path("<uuid:request_id>/quotes/", ServiceRequestQuoteListView.as_view(), name="service-request-quotes"),
]
