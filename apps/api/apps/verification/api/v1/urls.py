from django.urls import path

from apps.verification.api.v1.views import DocumentDownloadView, VerificationView

urlpatterns = [
    path("", VerificationView.as_view(), name="verification"),
    path("documents/<uuid:document_id>/", DocumentDownloadView.as_view(), name="verification-document"),
]
