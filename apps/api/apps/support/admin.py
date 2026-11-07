from django.contrib import admin

from apps.support.models import Dispute, DisputeEvidence, SupportTicket


class DisputeEvidenceInline(admin.TabularInline):
    model = DisputeEvidence
    extra = 0
    readonly_fields = ("file_key",)


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("booking", "status", "opened_by", "opened_at")
    list_filter = ("status",)
    inlines = [DisputeEvidenceInline]


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "status", "priority", "opened_by", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("subject", "opened_by__email")
