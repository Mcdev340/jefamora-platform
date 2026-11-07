from django.contrib import admin

from apps.clients.models import Address, ClientProfile, Favorite


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name")
    search_fields = ("user__email", "company_name")
    inlines = [AddressInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("client", "professional", "created_at")
    search_fields = ("client__user__email", "professional__business_name")
