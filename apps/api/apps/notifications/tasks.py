"""Envoi différé, exécuté par Celery quand le worker est lancé."""

from apps.notifications.services import notify


def deliver_notification(recipient_id, kind, title, body=""):
    from apps.users.models import User

    recipient = User.objects.filter(pk=recipient_id).first()
    return notify(recipient=recipient, kind=kind, title=title, body=body)
