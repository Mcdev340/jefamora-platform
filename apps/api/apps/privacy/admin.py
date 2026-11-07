from django.contrib import admin

from apps.privacy.models import DataDeletionRequest, UserConsent


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "version", "granted", "created_at")
    list_filter = ("code", "granted")


@admin.register(DataDeletionRequest)
class DataDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "created_at")
    list_filter = ("status",)
