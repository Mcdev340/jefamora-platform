from django.contrib import admin

from apps.service_requests.models import RequestRecipient, ServiceRequest


class RequestRecipientInline(admin.TabularInline):
    model = RequestRecipient
    extra = 0


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "zone", "status", "urgency", "created_at")
    list_filter = ("status", "urgency")
    search_fields = ("title", "client__user__email")
    inlines = [RequestRecipientInline]
