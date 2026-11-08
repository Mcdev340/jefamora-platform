from rest_framework import serializers

from apps.locations.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "label", "city", "district", "latitude", "longitude")
