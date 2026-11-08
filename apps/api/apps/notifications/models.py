"""Notifications internes. L'envoi push et SMS reste branché plus tard."""

import uuid

from django.db import models


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    kind = models.CharField(max_length=64)
    title = models.CharField(max_length=180)
    body = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "is_read"])]
        verbose_name = "notification"

    def __str__(self):
        return self.title


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="notification_preference",
    )
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = "préférence de notification"

    def __str__(self):
        return str(self.user_id)
