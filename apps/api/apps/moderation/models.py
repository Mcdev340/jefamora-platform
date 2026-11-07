"""Signalements, modération et blocages."""

import uuid

from django.db import models


class Report(models.Model):
    class Target(models.TextChoices):
        PROFILE = "professional_profile", "Profil"
        REVIEW = "review", "Avis"
        MESSAGE = "message", "Message"
        PORTFOLIO = "portfolio_item", "Réalisation"

    class Reason(models.TextChoices):
        FRAUD = "fraud", "Contenu mensonger"
        ABUSE = "abuse", "Comportement abusif"
        INAPPROPRIATE = "inappropriate", "Contenu inapproprié"
        OTHER = "other", "Autre"

    class Status(models.TextChoices):
        OPEN = "open", "Ouvert"
        REJECTED = "rejected", "Classé sans suite"
        ACTION_TAKEN = "action_taken", "Traité"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="reports_filed",
    )
    target_type = models.CharField(max_length=40, choices=Target.choices)
    target_id = models.UUIDField()
    reason = models.CharField(max_length=32, choices=Reason.choices)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "signalement"

    def __str__(self):
        return f"{self.get_target_type_display()} {self.status}"


class ModerationAction(models.Model):
    class Action(models.TextChoices):
        HIDE = "hide", "Masquer"
        DELETE = "delete", "Supprimer de l'affichage"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        Report,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="actions",
    )
    moderator = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="moderation_actions",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    target_type = models.CharField(max_length=40)
    target_id = models.UUIDField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "action de modération"

    def __str__(self):
        return self.get_action_display()


class UserBlock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blocker = models.ForeignKey(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="blocks_made",
    )
    blocked = models.ForeignKey(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="blocks_received",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["blocker", "blocked"], name="unique_user_block"),
            models.CheckConstraint(
                condition=~models.Q(blocker=models.F("blocked")),
                name="cannot_block_self",
            ),
        ]
        verbose_name = "blocage"

    def __str__(self):
        return f"{self.blocker_id} bloque {self.blocked_id}"
