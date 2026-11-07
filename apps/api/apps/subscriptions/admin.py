from django.contrib import admin

from apps.subscriptions.models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("professional", "plan", "status", "starts_at", "ends_at")
    list_filter = ("status", "plan")
