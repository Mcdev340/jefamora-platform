from django.contrib import admin

from apps.quotes.models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("service_request", "recipient", "total_amount", "status", "expires_at")
    list_filter = ("status",)
    search_fields = ("service_request__title", "recipient__professional__business_name")
