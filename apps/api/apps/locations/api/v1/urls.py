from django.urls import path

from apps.locations.api.v1.views import AddressDetailView, AddressListView

urlpatterns = [
    path("addresses/", AddressListView.as_view(), name="addresses"),
    path("addresses/<uuid:pk>/", AddressDetailView.as_view(), name="address"),
]
