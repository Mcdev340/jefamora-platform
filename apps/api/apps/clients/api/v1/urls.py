from django.urls import path

from apps.clients.api.v1.views import ClientProfileView

urlpatterns = [
    path("me/", ClientProfileView.as_view(), name="client-profile"),
]
