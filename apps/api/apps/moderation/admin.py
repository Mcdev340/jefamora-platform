from django.contrib import admin

from apps.moderation.models import ModerationAction, Report, UserBlock


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("target_type", "reason", "status", "reporter", "created_at")
    list_filter = ("status", "reason", "target_type")
    search_fields = ("description", "reporter__email")


@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    list_display = ("action", "target_type", "moderator", "created_at")
    search_fields = ("reason", "moderator__email")


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ("blocker", "blocked", "created_at")
    search_fields = ("blocker__email", "blocked__email")
