from django.core.exceptions import ValidationError

from apps.users.models import User


def validate_client_user(user):
    if user is None:
        return
    if user.role != User.Role.CLIENT:
        raise ValidationError(
            {"user": "Un profil client appartient à un compte client."}
        )
