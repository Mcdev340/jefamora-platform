from django.urls import path

from apps.catalog.api.v1.views import CategoryListView, SpecialtyListView, TradeListView, ZoneListView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="catalog-categories"),
    path("trades/", TradeListView.as_view(), name="catalog-trades"),
    path("specialties/", SpecialtyListView.as_view(), name="catalog-specialties"),
    path("zones/", ZoneListView.as_view(), name="catalog-zones"),
]
