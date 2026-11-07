"""Consentements et demandes de suppression."""

import uuid

from django.db import models


class UserConsent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="consents",
    )
    code = models.CharField(max_length=40)
    version = models.CharField(max_length=20, default="v1")
    granted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "consentement"

    def __str__(self):
        return f"{self.code} {self.user_id}"


class DataDeletionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        BLOCKED = "blocked", "Bloquée par une obligation"
        COMPLETED = "completed", "Traitée"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="deletion_requests",
    )
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "demande de suppression"

    def __str__(self):
        return f"{self.user_id} {self.status}"
