from django.urls import path

from apps.bookings.api.v1.views import (
    BookingConfirmCompletionView,
    BookingDetailView,
    BookingDisputeView,
    BookingListView,
    BookingRequestCompletionView,
    BookingStartView,
)

urlpatterns = [
    path("", BookingListView.as_view(), name="bookings"),
    path("<uuid:booking_id>/", BookingDetailView.as_view(), name="booking"),
    path("<uuid:booking_id>/start/", BookingStartView.as_view(), name="booking-start"),
    path("<uuid:booking_id>/request-completion/", BookingRequestCompletionView.as_view(), name="booking-request-completion"),
    path("<uuid:booking_id>/confirm-completion/", BookingConfirmCompletionView.as_view(), name="booking-confirm-completion"),
    path("<uuid:booking_id>/disputes/", BookingDisputeView.as_view(), name="booking-dispute"),
]
