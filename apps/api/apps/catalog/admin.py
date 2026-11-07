from django.contrib import admin

from apps.catalog.models import Category, Specialty, Trade


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("name", "trade", "is_active")
    list_filter = ("trade", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
