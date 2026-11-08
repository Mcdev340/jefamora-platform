from django.db.models import Q

from apps.audit.services import audit
from apps.messaging.models import Message
from apps.core.exceptions import APIError
from apps.moderation.models import ModerationAction, Report, UserBlock
from apps.notifications.services import notify
from apps.portfolio.models import PortfolioItem
from apps.reviews.models import Review


def users_are_blocked(first_id, second_id):
    return UserBlock.objects.filter(
        Q(blocker_id=first_id, blocked_id=second_id) | Q(blocker_id=second_id, blocked_id=first_id)
    ).exists()


def block_user(*, blocker, blocked_id):
    if blocker.id == blocked_id:
        raise APIError("validation_error", "Vous ne pouvez pas vous bloquer.")
    block, _created = UserBlock.objects.get_or_create(blocker=blocker, blocked_id=blocked_id)
    return block


def unblock_user(*, blocker, blocked_id):
    UserBlock.objects.filter(blocker=blocker, blocked_id=blocked_id).delete()


def file_report(*, reporter, target_type, target_id, reason, description=""):
    if target_type not in Report.Target.values:
        raise APIError("validation_error", "Cible de signalement inconnue.", fields={"target_type": ["Invalide."]})
    report = Report.objects.create(
        reporter=reporter,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
        description=description,
    )
    notify(
        recipient=reporter,
        kind="report_opened",
        title="Signalement envoyé",
        body="L'équipe Jefamora va l'examiner.",
        payload={"report_id": str(report.id)},
    )
    audit(actor=reporter, action="report.opened", target=report)
    return report


def close_report(*, report, admin):
    report.status = Report.Status.REJECTED
    report.save(update_fields=["status"])
    audit(actor=admin, action="report.closed", target=report)
    return report


def moderate_target(*, admin, target_type, target_id, action, reason, report=None):
    if target_type == Report.Target.PORTFOLIO:
        item = PortfolioItem.objects.get(pk=target_id)
        item.status = PortfolioItem.Status.REJECTED
        item.save(update_fields=["status", "updated_at"])
    elif target_type == Report.Target.REVIEW:
        review = Review.objects.select_related("booking__professional").get(pk=target_id)
        review.status = Review.Status.HIDDEN
        review.save(update_fields=["status", "updated_at"])
    elif target_type == Report.Target.MESSAGE:
        message = Message.objects.get(pk=target_id)
        message.is_hidden = True
        message.save(update_fields=["is_hidden", "updated_at"])
    elif target_type == Report.Target.PROFILE:
        from apps.professionals.models import ProfessionalProfile

        profile = ProfessionalProfile.objects.get(pk=target_id)
        profile.is_verified = False
        profile.save(update_fields=["is_verified", "updated_at"])
    else:
        raise APIError("validation_error", "Cible inconnue.")
    moderation = ModerationAction.objects.create(
        report=report,
        moderator=admin,
        action=action,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
    )
    if report is not None:
        report.status = Report.Status.ACTION_TAKEN
        report.save(update_fields=["status"])
    audit(actor=admin, action=f"moderation.{action}", target=moderation, metadata={"reason": reason})
    return moderation


def suspend_user(*, admin, user, active):
    user.is_active = active
    user.save(update_fields=["is_active", "updated_at"])
    action = "user.reactivated" if active else "user.suspended"
    if not active:
        notify(recipient=user, kind="account_suspended", title="Compte suspendu", body="Votre accès est suspendu.")
    audit(actor=admin, action=action, target=user)
    return user
