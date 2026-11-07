from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import UUIDModel
from apps.quotes.models import Quote


class Booking(UUIDModel):
    """Mission créée à partir du devis accepté.

    Il n'y a pas d'autre chemin : la demande et les personnes sont copiées
    depuis ce devis. Une demande ne donne qu'une réservation.
    """

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmée"
        IN_PROGRESS = "in_progress", "En cours"
        COMPLETED_BY_PROFESSIONAL = "completed_by_professional", "Fin déclarée par le professionnel"
        CONFIRMED_BY_CLIENT = "confirmed_by_client", "Confirmée par le client"
        CANCELLED = "cancelled", "Annulée"
        DISPUTED = "disputed", "En litige"

    quote = models.OneToOneField(
        "quotes.Quote",
        verbose_name="devis accepté",
        on_delete=models.PROTECT,
        related_name="booking",
    )
    service_request = models.OneToOneField(
        "service_requests.ServiceRequest",
        verbose_name="demande",
        on_delete=models.PROTECT,
        related_name="booking",
    )
    client = models.ForeignKey(
        "clients.ClientProfile",
        verbose_name="client",
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        verbose_name="professionnel",
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    status = models.CharField(
        "statut",
        max_length=40,
        choices=Status.choices,
        default=Status.CONFIRMED,
        db_index=True,
    )
    scheduled_at = models.DateTimeField("prévue le", null=True, blank=True)
    completed_at = models.DateTimeField("terminée le", null=True, blank=True)

    class Meta:
        verbose_name = "réservation"
        verbose_name_plural = "réservations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Réservation {self.service_request}"

    def prepare_save(self):
        if not self.quote_id:
            return
        quote = self.quote
        self.service_request_id = quote.service_request_id
        self.client_id = quote.service_request.client_id
        self.professional_id = quote.recipient.professional_id

    def clean(self):
        super().clean()
        if self.quote_id and self.quote.status != Quote.Status.ACCEPTED:
            raise ValidationError("Seul un devis accepté devient une réservation.")
