from django.contrib import admin

from apps.clients.models import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name")
    search_fields = ("user__email", "company_name")
