from rest_framework import generics

from apps.core.permissions import IsClient
from apps.locations.api.v1.serializers import AddressSerializer
from apps.locations.models import Address


class AddressListView(generics.ListCreateAPIView):
    permission_classes = [IsClient]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(client=self.request.user.client_profile)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client_profile)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsClient]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(client=self.request.user.client_profile)
