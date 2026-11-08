from django.urls import path

from apps.reviews.api.v1.views import ReviewCreateView, ReviewDetailView

urlpatterns = [
    path("", ReviewCreateView.as_view(), name="reviews"),
    path("<uuid:review_id>/", ReviewDetailView.as_view(), name="review"),
]
