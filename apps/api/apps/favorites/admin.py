from django.contrib import admin

from apps.favorites.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("client", "professional", "created_at")
    search_fields = ("client__user__email", "professional__business_name")
