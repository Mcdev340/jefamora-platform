from django.contrib import admin

from apps.verification.models import IdentityDocument, VerificationCase, VerificationDecision


class IdentityDocumentInline(admin.TabularInline):
    model = IdentityDocument
    extra = 0
    readonly_fields = ("private_file_key",)


class VerificationDecisionInline(admin.TabularInline):
    model = VerificationDecision
    extra = 0
    readonly_fields = ("decided_at",)


@admin.register(VerificationCase)
class VerificationCaseAdmin(admin.ModelAdmin):
    list_display = ("professional", "status", "submitted_at")
    list_filter = ("status",)
    search_fields = ("professional__business_name", "professional__user__email")
    inlines = [IdentityDocumentInline, VerificationDecisionInline]
