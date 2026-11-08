from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.bookings.models import Booking
from apps.messaging.services import open_conversation


@receiver(post_save, sender=Booking, dispatch_uid="jefamora.booking_opens_conversation")
def open_conversation_on_booking(sender, instance, created, **kwargs):
    if created:
        open_conversation(instance)
