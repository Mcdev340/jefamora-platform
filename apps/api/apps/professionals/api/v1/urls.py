from django.urls import path

from apps.professionals.api.v1.views import (
    AvailabilityDetailView,
    AvailabilityListCreateView,
    OwnProfileView,
    OwnZoneView,
    ProfessionalDetailView,
    ProfessionalListView,
    ServiceDetailView,
    ServiceListCreateView,
)

urlpatterns = [
    path("", ProfessionalListView.as_view(), name="professionals"),
    path("me/", OwnProfileView.as_view(), name="professionals-me"),
    path("me/zones/", OwnZoneView.as_view(), name="professionals-zones"),
    path("me/services/", ServiceListCreateView.as_view(), name="professionals-services"),
    path("me/services/<uuid:pk>/", ServiceDetailView.as_view(), name="professionals-service"),
    path("me/availabilities/", AvailabilityListCreateView.as_view(), name="professionals-availabilities"),
    path("me/availabilities/<uuid:pk>/", AvailabilityDetailView.as_view(), name="professionals-availability"),
    path("search/", ProfessionalListView.as_view(), name="search-professionals"),
    path("<uuid:profile_id>/", ProfessionalDetailView.as_view(), name="professionals-detail"),
]
