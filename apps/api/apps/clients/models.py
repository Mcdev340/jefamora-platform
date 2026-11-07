from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.clients.validators import validate_client_user
from apps.core.models import UUIDModel


class ClientProfile(UUIDModel):
    user = models.OneToOneField(
        "identity.User",
        verbose_name="compte",
        on_delete=models.PROTECT,
        related_name="client_profile",
    )
    company_name = models.CharField(
        "raison sociale",
        max_length=180,
        blank=True,
        help_text="Renseigné lorsque le client est une entreprise.",
    )

    class Meta:
        verbose_name = "profil client"
        verbose_name_plural = "profils clients"

    def __str__(self):
        return self.company_name or self.user.email

    def clean(self):
        super().clean()
        if self.user_id:
            validate_client_user(self.user)


class Address(UUIDModel):
    client = models.ForeignKey(
        ClientProfile,
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


class Favorite(UUIDModel):
    client = models.ForeignKey(
        ClientProfile,
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
