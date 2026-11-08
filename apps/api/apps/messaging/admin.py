from django.contrib import admin

from apps.messaging.models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("booking", "created_at")
    search_fields = ("booking__service_request__title",)
    inlines = [MessageInline]
