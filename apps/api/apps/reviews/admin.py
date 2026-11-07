from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "rating", "status", "editable_until", "created_at")
    list_filter = ("status", "rating")
    search_fields = ("comment", "booking__professional__business_name")
