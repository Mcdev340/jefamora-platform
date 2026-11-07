from apps.notifications.models import Notification


def notify(*, recipient, kind, title, body="", payload=None):
    if recipient is None:
        return None
    return Notification.objects.create(
        recipient=recipient,
        kind=kind,
        title=title,
        body=body,
        payload=payload or {},
    )
