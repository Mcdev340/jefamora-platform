from django.urls import path

from apps.professionals.api.v1.views import (
    AvailabilityDetailView,
    AvailabilityListCreateView,
    OwnProfileView,
    OwnZoneView,
    PortfolioDetailView,
    PortfolioListCreateView,
    PortfolioMediaCreateView,
    PortfolioMediaDownloadView,
    PortfolioPublishView,
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
    path("me/portfolio/", PortfolioListCreateView.as_view(), name="professionals-portfolio"),
    path("me/portfolio/<uuid:pk>/", PortfolioDetailView.as_view(), name="professionals-portfolio-item"),
    path("me/portfolio/<uuid:item_id>/media/", PortfolioMediaCreateView.as_view(), name="professionals-portfolio-media"),
    path("me/portfolio/<uuid:item_id>/publish/", PortfolioPublishView.as_view(), name="professionals-portfolio-publish"),
    path("portfolio/media/<uuid:media_id>/", PortfolioMediaDownloadView.as_view(), name="professionals-portfolio-file"),
    path("<uuid:profile_id>/", ProfessionalDetailView.as_view(), name="professionals-detail"),
]
