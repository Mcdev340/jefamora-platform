from django.db import models

from apps.core.models import UUIDModel
from apps.locations.validators import validate_zone_is_active
from apps.professionals.validators import validate_specialty_belongs_to_trade


class PortfolioItem(UUIDModel):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente de modération"
        PUBLISHED = "published", "Publiée"
        REJECTED = "rejected", "Refusée"

    profile = models.ForeignKey(
        "professionals.ProfessionalProfile",
        verbose_name="professionnel",
        on_delete=models.CASCADE,
        related_name="portfolio_items",
    )
    trade = models.ForeignKey(
        "catalog.Trade",
        verbose_name="métier",
        on_delete=models.PROTECT,
        related_name="portfolio_items",
        help_text="Métier du catalogue, le même référentiel que les services.",
    )
    specialty = models.ForeignKey(
        "catalog.Specialty",
        verbose_name="spécialité",
        on_delete=models.PROTECT,
        related_name="portfolio_items",
        null=True,
        blank=True,
    )
    zone = models.ForeignKey(
        "locations.Zone",
        verbose_name="zone générale",
        on_delete=models.PROTECT,
        related_name="portfolio_items",
        null=True,
        blank=True,
        help_text="Quartier ou ville du référentiel. Jamais une adresse précise.",
    )
    title = models.CharField("titre", max_length=180)
    description = models.TextField("description", blank=True)
    status = models.CharField(
        "statut",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    class Meta:
        verbose_name = "réalisation"
        verbose_name_plural = "réalisations"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        trade = self.trade if self.trade_id else None
        specialty = self.specialty if self.specialty_id else None
        validate_specialty_belongs_to_trade(trade, specialty)
        if self.zone_id:
            validate_zone_is_active(self.zone)


class PortfolioMedia(UUIDModel):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        BEFORE = "before", "Avant"
        AFTER = "after", "Après"

    item = models.ForeignKey(
        PortfolioItem,
        verbose_name="réalisation",
        on_delete=models.CASCADE,
        related_name="media",
    )
    media_type = models.CharField(
        "type",
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    file_key = models.CharField(
        "clé de fichier",
        max_length=500,
        help_text="Clé du stockage privé, pas une URL publique.",
    )
    display_order = models.PositiveIntegerField("ordre", default=0)

    class Meta:
        verbose_name = "média"
        verbose_name_plural = "médias"
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return f"{self.get_media_type_display()} — {self.item}"
