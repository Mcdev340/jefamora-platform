from django.urls import path

from apps.notifications.api.v1.views import NotificationListView, NotificationReadView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications"),
    path("<uuid:notification_id>/read/", NotificationReadView.as_view(), name="notification-read"),
]
