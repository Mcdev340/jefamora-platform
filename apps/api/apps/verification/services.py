from django.db import transaction

from apps.audit.services import audit
from apps.core.exceptions import APIError
from apps.core.files import store_private_file
from apps.notifications.services import notify
from apps.professionals.models import ProfessionalProfile
from apps.verification.models import IdentityDocument, VerificationCase, VerificationDecision


def _profile(user):
    try:
        return user.professional_profile
    except ProfessionalProfile.DoesNotExist as exc:
        raise APIError("forbidden", "Profil professionnel introuvable.", status_code=403) from exc


def _sync_profile(profile, status, badge):
    profile.verification_status = status
    profile.is_verified = badge
    profile.save(update_fields=["verification_status", "is_verified", "updated_at"])


@transaction.atomic
def upload_document(*, user, document_type, uploaded):
    profile = _profile(user)
    case = (
        profile.verification_cases.exclude(status=VerificationCase.Status.APPROVED)
        .order_by("-submitted_at")
        .first()
    )
    if case is None:
        case = VerificationCase.objects.create(
            professional=profile,
            status=VerificationCase.Status.DRAFT,
        )
    key = store_private_file(uploaded, "verification")
    return IdentityDocument.objects.create(
        case=case,
        document_type=document_type,
        private_file_key=key,
        original_name=uploaded.name[:180],
    )


@transaction.atomic
def submit_case(*, user):
    profile = _profile(user)
    case = profile.verification_cases.order_by("-submitted_at").first()
    if case is None or not case.documents.exists():
        raise APIError("validation_error", "Ajoutez au moins une pièce avant d'envoyer le dossier.")
    if case.status == VerificationCase.Status.APPROVED:
        raise APIError("invalid_transition", "Ce dossier est déjà validé.")
    if case.status == VerificationCase.Status.PENDING:
        return case
    case.status = VerificationCase.Status.PENDING
    case.admin_comment = ""
    case.save(update_fields=["status", "admin_comment", "updated_at"])
    _sync_profile(profile, ProfessionalProfile.VerificationStatus.PENDING, False)
    audit(actor=user, action="verification.submitted", target=case)
    return case


@transaction.atomic
def decide_case(*, case, admin, decision, comment=""):
    if case.status != VerificationCase.Status.PENDING:
        raise APIError("invalid_transition", "Ce dossier n'est plus en attente.")
    if not comment and decision != VerificationDecision.Decision.APPROVED:
        raise APIError("validation_error", "Un motif est obligatoire.", fields={"comment": ["Obligatoire."]})
    case.status = decision
    case.admin_comment = comment
    case.save(update_fields=["status", "admin_comment", "updated_at"])
    profile = case.professional
    if decision == VerificationDecision.Decision.APPROVED:
        _sync_profile(profile, ProfessionalProfile.VerificationStatus.APPROVED, True)
        title = "Profil vérifié Jefamora"
        body = "Votre dossier est validé. Votre fiche est visible."
    elif decision == VerificationDecision.Decision.NEEDS_COMPLEMENT:
        _sync_profile(profile, ProfessionalProfile.VerificationStatus.NEEDS_COMPLEMENT, False)
        title = "Complément demandé"
        body = comment
    else:
        _sync_profile(profile, ProfessionalProfile.VerificationStatus.REJECTED, False)
        title = "Dossier refusé"
        body = comment
    VerificationDecision.objects.create(
        case=case,
        decided_by=admin,
        decision=decision,
        comment=comment,
    )
    notify(
        recipient=profile.user,
        kind="verification_decision",
        title=title,
        body=body,
        payload={"case_id": str(case.id), "decision": decision},
    )
    audit(actor=admin, action=f"verification.{decision}", target=case, metadata={"comment": comment})
    return case
