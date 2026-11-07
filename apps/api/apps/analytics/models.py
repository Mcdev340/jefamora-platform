"""Exports demandés par l'administration."""

import uuid

from django.db import models


class AnalyticsExport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requested_by = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="analytics_exports",
    )
    export_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "export"

    def __str__(self):
        return self.export_type
