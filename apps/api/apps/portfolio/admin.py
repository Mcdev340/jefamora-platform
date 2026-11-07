from django.contrib import admin

from apps.portfolio.models import PortfolioItem, PortfolioMedia


class PortfolioMediaInline(admin.TabularInline):
    model = PortfolioMedia
    extra = 0


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("title", "profile", "trade", "zone", "status")
    list_filter = ("status", "trade")
    search_fields = ("title", "profile__business_name")
    inlines = [PortfolioMediaInline]
