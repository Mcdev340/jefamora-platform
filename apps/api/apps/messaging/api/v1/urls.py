from django.urls import path

from apps.messaging.api.v1.views import MessageListCreateView

urlpatterns = [
    path("<uuid:conversation_id>/messages/", MessageListCreateView.as_view(), name="conversation-messages"),
]
