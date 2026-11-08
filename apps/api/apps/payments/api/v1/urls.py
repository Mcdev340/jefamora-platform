from django.urls import path

from apps.payments.api.v1.views import InactiveModuleView

urlpatterns = [
    path("", InactiveModuleView.as_view(), name="payments"),
]
