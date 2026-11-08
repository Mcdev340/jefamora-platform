from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.quotes.models import Quote, QuoteLine
from apps.service_requests.models import RequestRecipient, ServiceRequest


class RecipientSerializer(serializers.ModelSerializer):
    professional_name = serializers.CharField(source="professional.business_name", read_only=True)

    class Meta:
        model = RequestRecipient
        fields = ("id", "professional", "professional_name", "status", "decline_reason", "created_at")


class ServiceRequestSerializer(serializers.ModelSerializer):
    recipients = RecipientSerializer(many=True, read_only=True)
    booking_id = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = (
            "id",
            "zone",
            "title",
            "description",
            "status",
            "urgency",
            "budget",
            "desired_date",
            "recipients",
            "booking_id",
            "created_at",
        )
        read_only_fields = ("status", "created_at")

    def get_booking_id(self, obj):
        try:
            return str(obj.booking.id)
        except ObjectDoesNotExist:
            return None


class ServiceRequestCreateSerializer(serializers.Serializer):
    zone = serializers.UUIDField()
    title = serializers.CharField(max_length=180)
    description = serializers.CharField()
    professional_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)
    urgency = serializers.ChoiceField(choices=ServiceRequest.Urgency.choices, required=False)
    budget = serializers.DecimalField(max_digits=12, decimal_places=0, required=False, allow_null=True)
    desired_date = serializers.DateTimeField(required=False, allow_null=True)


class DeclineSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class QuoteLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteLine
        fields = ("id", "label", "quantity", "unit_price")


class QuoteSerializer(serializers.ModelSerializer):
    lines = QuoteLineSerializer(many=True, read_only=True)

    class Meta:
        model = Quote
        fields = (
            "id",
            "recipient",
            "service_request",
            "total_amount",
            "status",
            "estimated_delay",
            "conditions",
            "expires_at",
            "lines",
            "created_at",
        )


class QuoteCreateSerializer(serializers.Serializer):
    service_request = serializers.UUIDField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=0)
    estimated_delay = serializers.CharField(required=False, allow_blank=True)
    conditions = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    lines = QuoteLineSerializer(many=True, required=False)
