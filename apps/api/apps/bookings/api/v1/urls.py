from django.urls import path

from apps.bookings.api.v1.views import (
    BookingConfirmCompletionView,
    BookingDetailView,
    BookingDisputeView,
    BookingListView,
    BookingRequestCompletionView,
    BookingStartView,
    DisputeEvidenceView,
    MessageListCreateView,
    ReviewCreateView,
    ReviewDetailView,
)
from apps.service_requests.api.v1.views import (
    QuoteAcceptView,
    QuoteCreateView,
    QuoteRejectView,
    ServiceRequestAttachmentView,
    ServiceRequestCancelView,
    ServiceRequestDeclineView,
    ServiceRequestDetailView,
    ServiceRequestListCreateView,
    ServiceRequestQuoteListView,
)

service_request_patterns = [
    path("", ServiceRequestListCreateView.as_view(), name="service-requests"),
    path("<uuid:request_id>/", ServiceRequestDetailView.as_view(), name="service-request"),
    path("<uuid:request_id>/cancel/", ServiceRequestCancelView.as_view(), name="service-request-cancel"),
    path("<uuid:request_id>/decline/", ServiceRequestDeclineView.as_view(), name="service-request-decline"),
    path("<uuid:request_id>/attachments/", ServiceRequestAttachmentView.as_view(), name="service-request-attachment"),
    path("<uuid:request_id>/quotes/", ServiceRequestQuoteListView.as_view(), name="service-request-quotes"),
]

quote_patterns = [
    path("", QuoteCreateView.as_view(), name="quotes"),
    path("<uuid:quote_id>/accept/", QuoteAcceptView.as_view(), name="quote-accept"),
    path("<uuid:quote_id>/reject/", QuoteRejectView.as_view(), name="quote-reject"),
]

booking_patterns = [
    path("", BookingListView.as_view(), name="bookings"),
    path("<uuid:booking_id>/", BookingDetailView.as_view(), name="booking"),
    path("<uuid:booking_id>/start/", BookingStartView.as_view(), name="booking-start"),
    path("<uuid:booking_id>/request-completion/", BookingRequestCompletionView.as_view(), name="booking-request-completion"),
    path("<uuid:booking_id>/confirm-completion/", BookingConfirmCompletionView.as_view(), name="booking-confirm-completion"),
    path("<uuid:booking_id>/disputes/", BookingDisputeView.as_view(), name="booking-dispute"),
]

conversation_patterns = [
    path("<uuid:conversation_id>/messages/", MessageListCreateView.as_view(), name="conversation-messages"),
]

review_patterns = [
    path("", ReviewCreateView.as_view(), name="reviews"),
    path("<uuid:review_id>/", ReviewDetailView.as_view(), name="review"),
]

dispute_patterns = [
    path("<uuid:dispute_id>/evidence/", DisputeEvidenceView.as_view(), name="dispute-evidence"),
]
