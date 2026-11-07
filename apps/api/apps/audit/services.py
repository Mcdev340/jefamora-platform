from apps.audit.models import AuditLog, SecurityEvent
from apps.core.request import client_ip


def audit(*, actor, action, target=None, metadata=None, request=None):
    target_type = ""
    target_id = None
    if target is not None:
        target_type = target._meta.label_lower
        target_id = target.pk
    return AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata=metadata or {},
        ip_address=client_ip(request),
    )


def security_event(*, kind, user=None, request=None, detail=""):
    return SecurityEvent.objects.create(
        user=user if getattr(user, "pk", None) else None,
        kind=kind,
        ip_address=client_ip(request),
        detail=detail[:255],
    )
