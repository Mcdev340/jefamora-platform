from django.urls import path

from apps.portfolio.api.v1.views import (
    PortfolioDetailView,
    PortfolioListCreateView,
    PortfolioMediaCreateView,
    PortfolioMediaDownloadView,
    PortfolioPublishView,
)

urlpatterns = [
    path("", PortfolioListCreateView.as_view(), name="professionals-portfolio"),
    path("<uuid:pk>/", PortfolioDetailView.as_view(), name="professionals-portfolio-item"),
    path("<uuid:item_id>/media/", PortfolioMediaCreateView.as_view(), name="professionals-portfolio-media"),
    path("<uuid:item_id>/publish/", PortfolioPublishView.as_view(), name="professionals-portfolio-publish"),
    path("media/<uuid:media_id>/", PortfolioMediaDownloadView.as_view(), name="professionals-portfolio-file"),
]
