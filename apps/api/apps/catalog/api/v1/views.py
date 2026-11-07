from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.catalog.api.v1.serializers import (
    CategorySerializer,
    SpecialtySerializer,
    TradeSerializer,
    ZoneSerializer,
)
from apps.catalog.models import Category, Specialty, Trade
from apps.locations.models import Zone


class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)


class TradeListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TradeSerializer
    queryset = Trade.objects.filter(is_active=True, category__is_active=True)
    filterset_fields = ("category",)


class SpecialtyListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = SpecialtySerializer
    queryset = Specialty.objects.filter(is_active=True, trade__is_active=True)
    filterset_fields = ("trade",)


class ZoneListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ZoneSerializer
    queryset = Zone.objects.filter(is_active=True)
    filterset_fields = ("region", "city")
