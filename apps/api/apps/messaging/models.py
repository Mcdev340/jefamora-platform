from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import UUIDModel


class Conversation(UUIDModel):
    """Fil unique d'une réservation. Il n'existe pas avant la mission."""

    booking = models.OneToOneField(
        "bookings.Booking",
        verbose_name="réservation",
        on_delete=models.PROTECT,
        related_name="conversation",
    )

    class Meta:
        verbose_name = "conversation"
        verbose_name_plural = "conversations"

    def __str__(self):
        return f"Conversation {self.booking_id}"


class Message(UUIDModel):
    conversation = models.ForeignKey(
        Conversation,
        verbose_name="conversation",
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        "identity.User",
        verbose_name="auteur",
        on_delete=models.PROTECT,
        related_name="sent_messages",
    )
    content = models.TextField("message")
    is_read = models.BooleanField("lu", default=False)
    is_hidden = models.BooleanField("masqué", default=False)

    class Meta:
        verbose_name = "message"
        verbose_name_plural = "messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"Message de {self.sender_id}"

    def clean(self):
        super().clean()
        if not self.conversation_id or not self.sender_id:
            return
        booking = self.conversation.booking
        participants = {booking.client.user_id, booking.professional.user_id}
        if self.sender_id not in participants:
            raise ValidationError(
                "Seuls le client et le professionnel de la mission peuvent écrire."
            )
