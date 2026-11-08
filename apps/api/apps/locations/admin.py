from django.contrib import admin

from apps.locations.models import Address, Zone


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("region", "city", "district", "is_active")
    list_filter = ("region", "is_active")
    search_fields = ("region", "city", "district")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("label", "city", "district", "client")
    search_fields = ("label", "city", "client__user__email")
