from django.contrib import admin

from apps.audit.models import AuditLog, SecurityEvent


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "target_type", "created_at")
    list_filter = ("action",)
    search_fields = ("action", "actor__email")
    readonly_fields = ("actor", "action", "target_type", "target_id", "metadata", "ip_address", "created_at")


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ("kind", "user", "ip_address", "created_at")
    list_filter = ("kind",)
    readonly_fields = ("user", "kind", "ip_address", "detail", "created_at")
