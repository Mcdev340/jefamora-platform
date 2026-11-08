from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import UUIDModel


class Zone(UUIDModel):
    """Zone tenue par l'administration.

    Le professionnel en coche, le client en choisit une pour sa demande.
    Il n'existe pas de seconde liste ni de saisie libre.
    """

    region = models.CharField("région", max_length=120)
    city = models.CharField("ville", max_length=120)
    district = models.CharField("quartier", max_length=120, blank=True, default="")
    is_active = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "zone"
        verbose_name_plural = "zones"
        ordering = ["region", "city", "district"]
        constraints = [
            models.UniqueConstraint(
                fields=["region", "city", "district"],
                name="unique_zone_region_city_district",
            ),
        ]
        indexes = [
            models.Index(fields=["city", "is_active"]),
        ]

    def __str__(self):
        place = f"{self.city} — {self.district}" if self.district else self.city
        return f"{place} ({self.region})"


class Address(UUIDModel):
    """Adresse du client. La zone de mission reste le référentiel Zone."""

    client = models.ForeignKey(
        "clients.ClientProfile",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    label = models.CharField("libellé", max_length=80)
    city = models.CharField("ville", max_length=120)
    district = models.CharField("quartier", max_length=120, blank=True)
    latitude = models.DecimalField(
        "latitude",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        "longitude",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    class Meta:
        verbose_name = "adresse"
        verbose_name_plural = "adresses"
        ordering = ["label"]

    def __str__(self):
        return f"{self.label} — {self.city}"
