from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.bookings.models import Booking
from apps.messaging.models import Message
from apps.reviews.models import Review


class BookingSerializer(serializers.ModelSerializer):
    conversation_id = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            "id",
            "quote",
            "service_request",
            "client",
            "professional",
            "status",
            "scheduled_at",
            "completed_at",
            "created_at",
            "conversation_id",
        )

    def get_conversation_id(self, obj):
        try:
            return str(obj.conversation.id)
        except ObjectDoesNotExist:
            return None


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "sender", "content", "is_read", "created_at")
        read_only_fields = ("sender", "is_read", "created_at")


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
            "id",
            "booking",
            "rating",
            "comment",
            "professional_reply",
            "status",
            "editable_until",
            "created_at",
        )
        read_only_fields = ("status", "editable_until", "created_at", "professional_reply")


class ReviewReplySerializer(serializers.Serializer):
    professional_reply = serializers.CharField()
