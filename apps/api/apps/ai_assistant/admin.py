from django.contrib import admin

from apps.ai_assistant.models import AssistantRequest


@admin.register(AssistantRequest)
class AssistantRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "created_at")
    list_filter = ("status",)
