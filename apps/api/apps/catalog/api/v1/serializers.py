from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.catalog.models import Category, Specialty, Trade
from apps.locations.models import Zone
from apps.portfolio.models import PortfolioItem, PortfolioMedia
from apps.professionals.models import Availability, ProfessionalProfile, ProfessionalService
from apps.reviews.models import Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "is_active")


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ("id", "category", "name", "slug", "is_active")


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ("id", "trade", "name", "slug", "is_active")


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ("id", "region", "city", "district", "is_active")


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalService
        fields = (
            "id",
            "trade",
            "specialty",
            "title",
            "description",
            "starting_price",
            "is_active",
        )


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ("id", "weekday", "start_time", "end_time", "is_available")


class PortfolioMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioMedia
        fields = ("id", "media_type", "file_key", "display_order")


class PortfolioSerializer(serializers.ModelSerializer):
    media = PortfolioMediaSerializer(many=True, read_only=True)

    class Meta:
        model = PortfolioItem
        fields = ("id", "trade", "specialty", "zone", "title", "description", "status", "media", "created_at")
        read_only_fields = ("status", "created_at")


class ReviewPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "rating", "comment", "professional_reply", "created_at")


class ProfessionalCardSerializer(serializers.ModelSerializer):
    zones = ZoneSerializer(many=True, read_only=True)

    class Meta:
        model = ProfessionalProfile
        fields = (
            "id",
            "business_name",
            "biography",
            "years_of_experience",
            "is_verified",
            "average_rating",
            "zones",
        )


class ProfessionalDetailSerializer(ProfessionalCardSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    availabilities = AvailabilitySerializer(many=True, read_only=True)
    portfolio = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta(ProfessionalCardSerializer.Meta):
        fields = ProfessionalCardSerializer.Meta.fields + (
            "services",
            "availabilities",
            "portfolio",
            "reviews",
        )

    def get_portfolio(self, obj):
        items = [item for item in obj.portfolio_items.all() if item.status == PortfolioItem.Status.PUBLISHED]
        return PortfolioSerializer(items, many=True).data

    def get_reviews(self, obj):
        reviews = []
        for booking in obj.bookings.all():
            try:
                review = booking.review
            except ObjectDoesNotExist:
                continue
            if review.status == Review.Status.PUBLISHED:
                reviews.append(review)
        return ReviewPublicSerializer(reviews, many=True).data
