from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import UUIDModel


class Quote(UUIDModel):
    """Proposition de prix d'un destinataire.

    Une demande peut en porter plusieurs. Un seul passe au statut accepté,
    et c'est celui-là qui devient la réservation.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        SENT = "sent", "Envoyé"
        ACCEPTED = "accepted", "Accepté"
        REFUSED = "refused", "Refusé"
        EXPIRED = "expired", "Expiré"

    recipient = models.ForeignKey(
        "service_requests.RequestRecipient",
        verbose_name="destinataire",
        on_delete=models.PROTECT,
        related_name="quotes",
    )
    service_request = models.ForeignKey(
        "service_requests.ServiceRequest",
        verbose_name="demande",
        on_delete=models.PROTECT,
        related_name="quotes",
        help_text="Toujours la demande du destinataire. Sert à garantir un seul devis accepté.",
    )
    total_amount = models.DecimalField(
        "montant total",
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Montant en francs CFA.",
    )
    status = models.CharField(
        "statut",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    estimated_delay = models.CharField("délai", max_length=120, blank=True)
    conditions = models.TextField("conditions", blank=True)
    expires_at = models.DateTimeField("expire le", null=True, blank=True)

    class Meta:
        verbose_name = "devis"
        verbose_name_plural = "devis"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["service_request"],
                condition=models.Q(status="accepted"),
                name="one_accepted_quote_per_request",
            ),
        ]

    def __str__(self):
        return f"Devis {self.total_amount} F CFA"

    def prepare_save(self):
        if self.recipient_id:
            self.service_request_id = self.recipient.service_request_id


class QuoteLine(UUIDModel):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="lines")
    label = models.CharField("libellé", max_length=180)
    quantity = models.DecimalField(
        "quantité",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    unit_price = models.DecimalField(
        "prix unitaire",
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Montant en francs CFA.",
    )

    class Meta:
        verbose_name = "ligne de devis"
        verbose_name_plural = "lignes de devis"
        ordering = ["created_at"]

    def __str__(self):
        return self.label


QuoteItem = QuoteLine
