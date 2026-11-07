from django.contrib import admin

from apps.analytics.models import AnalyticsExport


@admin.register(AnalyticsExport)
class AnalyticsExportAdmin(admin.ModelAdmin):
    list_display = ("export_type", "requested_by", "created_at")
    search_fields = ("export_type", "requested_by__email")
