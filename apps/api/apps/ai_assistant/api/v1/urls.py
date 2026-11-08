from django.urls import path

from apps.ai_assistant.api.v1.views import InactiveAssistantView

urlpatterns = [
    path("", InactiveAssistantView.as_view(), name="ai"),
]
