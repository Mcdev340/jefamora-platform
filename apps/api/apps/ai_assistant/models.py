"""Assistant, préparé pour un serveur distinct en V2."""

from django.db import models

from apps.core.models import UUIDModel


class AssistantRequest(UUIDModel):
    class Status(models.TextChoices):
        DISABLED = "disabled", "Inactif"

    user = models.ForeignKey(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="assistant_requests",
    )
    prompt = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DISABLED)

    class Meta:
        verbose_name = "demande d'assistant"

    def __str__(self):
        return self.status
