from django.contrib import admin

from apps.payments.models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "currency", "status", "created_at")
    list_filter = ("status",)
