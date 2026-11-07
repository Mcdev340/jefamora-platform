from django.core.exceptions import ValidationError


def validate_zone_is_active(zone):
    if zone is not None and not zone.is_active:
        raise ValidationError({"zone": "Cette zone n'est plus disponible."})
