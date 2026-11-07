"""Abonnements professionnels, préparés pour la V2."""

from django.db import models

from apps.core.models import UUIDModel


class Subscription(UUIDModel):
    class Status(models.TextChoices):
        INACTIVE = "inactive", "Inactif"
        ACTIVE = "active", "Actif"
        CANCELLED = "cancelled", "Annulé"

    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    plan = models.CharField(max_length=40, default="pro")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INACTIVE)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "abonnement"

    def __str__(self):
        return f"{self.professional} {self.plan}"
