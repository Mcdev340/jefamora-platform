from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone

from apps.bookings.models import Booking
from apps.core.models import UUIDModel


REVIEW_EDIT_WINDOW = timedelta(hours=48)


class Review(UUIDModel):
    """Avis unique d'une mission confirmée par le client.

    La réponse du professionnel est un champ du même avis.
    Le client peut changer la note et le commentaire pendant 48 heures.
    """

    class Status(models.TextChoices):
        PUBLISHED = "published", "Publié"
        HIDDEN = "hidden", "Masqué"

    booking = models.OneToOneField(
        "bookings.Booking",
        verbose_name="réservation",
        on_delete=models.PROTECT,
        related_name="review",
        help_text="Une mission confirmée donne un seul avis.",
    )
    author = models.ForeignKey(
        "identity.User",
        verbose_name="auteur",
        on_delete=models.PROTECT,
        related_name="reviews_written",
    )
    rating = models.PositiveSmallIntegerField(
        "note",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("commentaire", blank=True)
    professional_reply = models.TextField("réponse du professionnel", blank=True)
    status = models.CharField(
        "statut",
        max_length=20,
        choices=Status.choices,
        default=Status.PUBLISHED,
        db_index=True,
    )
    editable_until = models.DateTimeField(
        "modifiable jusqu'au",
        help_text="Le client peut modifier la note et le commentaire jusqu'à cette date.",
    )

    class Meta:
        verbose_name = "avis"
        verbose_name_plural = "avis"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"Avis {self.rating}/5"

    def prepare_save(self):
        if self._state.adding and self.editable_until is None:
            self.editable_until = timezone.now() + REVIEW_EDIT_WINDOW
        if self.booking_id:
            self.author_id = self.booking.client.user_id

    def clean(self):
        super().clean()
        if not self.booking_id:
            return
        if self.booking.status != Booking.Status.CONFIRMED_BY_CLIENT:
            raise ValidationError(
                "Un avis n'est possible qu'après confirmation de la mission par le client."
            )
        if self._state.adding:
            return
        previous = Review.objects.filter(pk=self.pk).only("rating", "comment", "editable_until").first()
        if previous is None or timezone.now() <= previous.editable_until:
            return
        if previous.rating != self.rating or previous.comment != self.comment:
            raise ValidationError(
                "L'avis ne peut plus être modifié après 48 heures."
            )

    def after_save(self):
        professional_id = self.booking.professional_id
        average = Review.objects.filter(
            booking__professional_id=professional_id,
            status=self.Status.PUBLISHED,
        ).aggregate(average=Avg("rating"))["average"]
        from apps.professionals.models import ProfessionalProfile

        stored = Decimal("0") if average is None else Decimal(average).quantize(Decimal("0.01"))
        ProfessionalProfile.objects.filter(pk=professional_id).update(
            average_rating=stored,
            updated_at=timezone.now(),
        )
