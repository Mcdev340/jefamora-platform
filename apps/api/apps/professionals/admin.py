from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from apps.professionals.models import Availability, ProfessionalProfile, ProfessionalService


class ProfessionalProfileAdminForm(forms.ModelForm):
    class Meta:
        model = ProfessionalProfile
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        zones = cleaned.get("zones")
        if zones is not None and zones.filter(is_active=False).exists():
            raise ValidationError(
                {"zones": "Un professionnel choisit une zone active du référentiel."}
            )
        return cleaned


class ProfessionalServiceInline(admin.TabularInline):
    model = ProfessionalService
    extra = 0


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0


@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    form = ProfessionalProfileAdminForm
    list_display = ("business_name", "user", "is_verified", "verification_status", "average_rating")
    list_filter = ("is_verified", "verification_status")
    search_fields = ("business_name", "user__email")
    filter_horizontal = ("zones",)
    inlines = [ProfessionalServiceInline, AvailabilityInline]
