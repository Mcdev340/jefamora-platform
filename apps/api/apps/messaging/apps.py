from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.messaging"
    label = "conversations"
    verbose_name = "Messagerie"

    def ready(self):
        from apps.messaging import signals  # noqa: F401
