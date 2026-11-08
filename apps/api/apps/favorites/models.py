from django.db import models

from apps.core.models import UUIDModel


class Favorite(UUIDModel):
    client = models.ForeignKey(
        "clients.ClientProfile",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        verbose_name="professionnel",
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )

    class Meta:
        verbose_name = "favori"
        verbose_name_plural = "favoris"
        constraints = [
            models.UniqueConstraint(
                fields=["client", "professional"],
                name="unique_favorite",
            ),
        ]

    def __str__(self):
        return f"{self.client} → {self.professional}"
