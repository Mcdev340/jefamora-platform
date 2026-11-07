"""Dossiers de vérification des professionnels."""

import uuid

from django.db import models

from apps.core.models import UUIDModel


class VerificationCase(UUIDModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        PENDING = "pending", "En attente"
        NEEDS_COMPLEMENT = "needs_complement", "À compléter"
        APPROVED = "approved", "Validé"
        REJECTED = "rejected", "Refusé"

    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="verification_cases",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    admin_comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "dossier de vérification"
        verbose_name_plural = "dossiers de vérification"

    def __str__(self):
        return f"{self.professional} — {self.get_status_display()}"


class IdentityDocument(UUIDModel):
    class DocumentType(models.TextChoices):
        NATIONAL_ID = "national_id", "Pièce d'identité"
        PROOF = "proof", "Justificatif"

    case = models.ForeignKey(
        VerificationCase,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(max_length=32, choices=DocumentType.choices)
    private_file_key = models.CharField(max_length=500)
    original_name = models.CharField(max_length=180, blank=True)

    class Meta:
        verbose_name = "pièce justificative"
        verbose_name_plural = "pièces justificatives"

    def __str__(self):
        return self.get_document_type_display()


class VerificationDecision(models.Model):
    class Decision(models.TextChoices):
        APPROVED = "approved", "Validé"
        NEEDS_COMPLEMENT = "needs_complement", "Complément"
        REJECTED = "rejected", "Refusé"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(
        VerificationCase,
        on_delete=models.CASCADE,
        related_name="decisions",
    )
    decided_by = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="verification_decisions",
    )
    decision = models.CharField(max_length=32, choices=Decision.choices)
    comment = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-decided_at"]
        verbose_name = "décision de vérification"

    def __str__(self):
        return self.get_decision_display()
