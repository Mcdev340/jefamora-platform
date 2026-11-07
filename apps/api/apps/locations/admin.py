from django.contrib import admin

from apps.locations.models import Zone


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("region", "city", "district", "is_active")
    list_filter = ("region", "is_active")
    search_fields = ("region", "city", "district")
