from django.urls import path

from apps.privacy.api.v1.views import ConsentView, DeletionView

urlpatterns = [
    path("consents/", ConsentView.as_view(), name="consents"),
    path("deletion-requests/", DeletionView.as_view(), name="deletion-requests"),
]
