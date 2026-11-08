from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import DeviceSession, OneTimeCode, User


@admin.register(User)
class JefamoraUserAdmin(UserAdmin):
    ordering = ["email"]
    list_display = ("email", "role", "is_verified", "is_active", "is_staff")
    list_filter = ("role", "is_verified", "is_active", "is_staff")
    search_fields = ("email", "phone", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profil", {"fields": ("first_name", "last_name", "phone", "role")}),
        ("Accès", {"fields": ("is_active", "is_verified", "is_staff", "is_superuser")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "is_staff"),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")


@admin.register(OneTimeCode)
class OneTimeCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "expires_at", "consumed_at")
    list_filter = ("purpose",)
    search_fields = ("user__email",)


@admin.register(DeviceSession)
class DeviceSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "revoked_at", "created_at")
    search_fields = ("user__email", "refresh_jti")
