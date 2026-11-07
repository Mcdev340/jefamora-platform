from datetime import time
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import UUIDModel
from apps.professionals.validators import (
    validate_professional_user,
    validate_specialty_belongs_to_trade,
)


class ProfessionalProfile(UUIDModel):
    """Fiche publique du professionnel.

    `is_verified` est le badge « Profil vérifié Jefamora ».
    Il est distinct de `User.is_verified`, qui confirme seulement l'e-mail.
    """

    class VerificationStatus(models.TextChoices):
        NOT_SUBMITTED = "not_submitted", "Non soumis"
        PENDING = "pending", "En attente"
        NEEDS_COMPLEMENT = "needs_complement", "Complément demandé"
        APPROVED = "approved", "Approuvé"
        REJECTED = "rejected", "Refusé"

    user = models.OneToOneField(
        "identity.User",
        verbose_name="compte",
        on_delete=models.PROTECT,
        related_name="professional_profile",
    )
    business_name = models.CharField("nom professionnel", max_length=180)
    biography = models.TextField("présentation", blank=True)
    years_of_experience = models.PositiveSmallIntegerField(
        "années d'expérience",
        null=True,
        blank=True,
    )
    is_verified = models.BooleanField(
        "badge vérifié",
        default=False,
        help_text="Badge Profil vérifié Jefamora. Il ne suit pas automatiquement le statut du dossier.",
    )
    verification_status = models.CharField(
        "statut du dossier",
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.NOT_SUBMITTED,
    )
    average_rating = models.DecimalField(
        "note moyenne",
        max_digits=3,
        decimal_places=2,
        default=Decimal("0"),
    )
    zones = models.ManyToManyField(
        "locations.Zone",
        verbose_name="zones couvertes",
        related_name="professionals",
        blank=True,
        help_text="Zones cochées dans le référentiel administré. Pas de saisie libre.",
    )

    class Meta:
        verbose_name = "profil professionnel"
        verbose_name_plural = "profils professionnels"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(average_rating__gte=0, average_rating__lte=5),
                name="professional_rating_between_0_and_5",
            ),
        ]
        indexes = [
            models.Index(fields=["is_verified", "verification_status"]),
        ]

    def __str__(self):
        return self.business_name

    def assign_zones(self, zones):
        """Remplace les zones couvertes par une sélection du référentiel actif."""

        selected = list(zones)
        if any(not zone.is_active for zone in selected):
            raise ValidationError(
                "Un professionnel choisit une zone active du référentiel."
            )
        self.zones.set(selected)

    def clean(self):
        super().clean()
        if self.user_id:
            validate_professional_user(self.user)


class ProfessionalService(UUIDModel):
    profile = models.ForeignKey(
        ProfessionalProfile,
        verbose_name="professionnel",
        on_delete=models.CASCADE,
        related_name="services",
    )
    trade = models.ForeignKey(
        "catalog.Trade",
        verbose_name="métier",
        on_delete=models.PROTECT,
        related_name="services",
        help_text="Métier du catalogue. La recherche s'appuie sur ce lien.",
    )
    specialty = models.ForeignKey(
        "catalog.Specialty",
        verbose_name="spécialité",
        on_delete=models.PROTECT,
        related_name="services",
        null=True,
        blank=True,
    )
    title = models.CharField("titre", max_length=180)
    description = models.TextField("description", blank=True)
    starting_price = models.DecimalField(
        "prix indicatif",
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Montant indicatif en francs CFA.",
    )
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "service"
        verbose_name_plural = "services"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        trade = self.trade if self.trade_id else None
        specialty = self.specialty if self.specialty_id else None
        validate_specialty_belongs_to_trade(trade, specialty)


class Availability(UUIDModel):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Lundi"
        TUESDAY = 1, "Mardi"
        WEDNESDAY = 2, "Mercredi"
        THURSDAY = 3, "Jeudi"
        FRIDAY = 4, "Vendredi"
        SATURDAY = 5, "Samedi"
        SUNDAY = 6, "Dimanche"

    profile = models.ForeignKey(
        ProfessionalProfile,
        verbose_name="professionnel",
        on_delete=models.CASCADE,
        related_name="availabilities",
    )
    weekday = models.IntegerField("jour", choices=Weekday.choices)
    start_time = models.TimeField("début", default=time(8, 0))
    end_time = models.TimeField("fin", default=time(18, 0))
    is_available = models.BooleanField("disponible", default=True)

    class Meta:
        verbose_name = "disponibilité"
        verbose_name_plural = "disponibilités"
        ordering = ["weekday", "start_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="availability_end_after_start",
            ),
            models.UniqueConstraint(
                fields=["profile", "weekday", "start_time", "end_time"],
                name="unique_availability_slot",
            ),
        ]

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}"

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError(
                {"end_time": "L'heure de fin doit être après l'heure de début."}
            )
