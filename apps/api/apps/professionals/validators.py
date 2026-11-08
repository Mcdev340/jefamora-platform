from django.core.exceptions import ValidationError


def validate_specialty_belongs_to_trade(trade, specialty):
    if trade is None or specialty is None:
        return
    if specialty.trade_id != trade.id:
        raise ValidationError(
            {"specialty": "La spécialité doit appartenir au métier choisi."}
        )


def validate_professional_user(user):
    from apps.users.models import User

    if user is None:
        return
    if user.role != User.Role.PROFESSIONAL:
        raise ValidationError(
            {"user": "Un profil professionnel appartient à un compte professionnel."}
        )
