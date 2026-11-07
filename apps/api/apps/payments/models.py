"""Paiement intégré, préparé pour la V2. Inactif au lancement."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import UUIDModel


class PaymentTransaction(UUIDModel):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        SUCCEEDED = "succeeded", "Réussie"
        FAILED = "failed", "Échouée"
        REFUNDED = "refunded", "Remboursée"

    booking = models.ForeignKey(
        "bookings.Booking",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="payment_transactions",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    currency = models.CharField(max_length=3, default="XOF")
    provider = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        verbose_name = "transaction de paiement"

    def __str__(self):
        return f"{self.amount} {self.currency}"
