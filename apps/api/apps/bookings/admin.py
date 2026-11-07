from django.contrib import admin

from apps.bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("service_request", "client", "professional", "status", "scheduled_at")
    list_filter = ("status",)
    search_fields = ("service_request__title", "professional__business_name", "client__user__email")
