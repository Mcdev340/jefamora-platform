from apps.messaging.models import Conversation


def open_conversation(booking):
    conversation, _created = Conversation.objects.get_or_create(booking=booking)
    return conversation
