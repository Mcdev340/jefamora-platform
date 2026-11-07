from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import UUIDModel
from apps.locations.validators import validate_zone_is_active


class ServiceRequest(UUIDModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        OPEN = "open", "Ouverte"
        QUOTED = "quoted", "Devis reçu"
        BOOKED = "booked", "Réservée"
        CANCELLED = "cancelled", "Annulée"
        CLOSED = "closed", "Clôturée"

    class Urgency(models.TextChoices):
        LOW = "low", "Faible"
        NORMAL = "normal", "Normale"
        URGENT = "urgent", "Urgente"

    client = models.ForeignKey(
        "clients.ClientProfile",
        verbose_name="client",
        on_delete=models.PROTECT,
        related_name="service_requests",
    )
    zone = models.ForeignKey(
        "locations.Zone",
        verbose_name="zone",
        on_delete=models.PROTECT,
        related_name="service_requests",
        help_text="Zone du référentiel, la même liste que la couverture des professionnels.",
    )
    title = models.CharField("titre", max_length=180)
    description = models.TextField("description")
    status = models.CharField(
        "statut",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    urgency = models.CharField(
        "urgence",
        max_length=20,
        choices=Urgency.choices,
        default=Urgency.NORMAL,
    )
    budget = models.DecimalField(
        "budget facultatif",
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Montant en francs CFA.",
    )
    desired_date = models.DateTimeField("créneau souhaité", null=True, blank=True)

    class Meta:
        verbose_name = "demande"
        verbose_name_plural = "demandes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.zone_id:
            validate_zone_is_active(self.zone)


class RequestRecipient(UUIDModel):
    """Un professionnel visé par une demande.

    Une demande en a plusieurs. Chacun peut refuser ou envoyer ses devis.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        QUOTED = "quoted", "Devis envoyé"
        REFUSED = "refused", "Refusé"
        ACCEPTED = "accepted", "Accepté"

    service_request = models.ForeignKey(
        ServiceRequest,
        verbose_name="demande",
        on_delete=models.CASCADE,
        related_name="recipients",
    )
    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        verbose_name="professionnel",
        on_delete=models.PROTECT,
        related_name="received_requests",
    )
    status = models.CharField(
        "statut",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    decline_reason = models.TextField("motif de refus", blank=True, default="")

    class Meta:
        verbose_name = "destinataire"
        verbose_name_plural = "destinataires"
        constraints = [
            models.UniqueConstraint(
                fields=["service_request", "professional"],
                name="one_recipient_per_professional",
            ),
        ]

    def __str__(self):
        return f"{self.professional} — {self.service_request}"


class RequestAttachment(UUIDModel):
    service_request = models.ForeignKey(
        ServiceRequest,
        verbose_name="demande",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file_key = models.CharField("clé de fichier", max_length=500)
    original_name = models.CharField("nom d'origine", max_length=180, blank=True)

    class Meta:
        verbose_name = "pièce jointe"
        verbose_name_plural = "pièces jointes"

    def __str__(self):
        return self.original_name or self.file_key
