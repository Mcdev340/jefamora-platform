from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from apps.audit.services import audit
from apps.core.exceptions import APIError
from apps.core.files import store_private_file
from apps.locations.models import Zone
from apps.notifications.services import notify
from apps.professionals.models import ProfessionalProfile
from apps.service_requests.models import RequestAttachment, RequestRecipient, ServiceRequest


@transaction.atomic
def create_service_request(*, client_user, zone_id, title, description, professional_ids, urgency, budget, desired_date):
    try:
        client = client_user.client_profile
    except ObjectDoesNotExist as exc:
        raise APIError("forbidden", "Profil client introuvable.", status_code=403) from exc
    try:
        zone = Zone.objects.get(pk=zone_id, is_active=True)
    except Zone.DoesNotExist as exc:
        raise APIError("validation_error", "Zone introuvable ou inactive.", fields={"zone": ["Invalide."]}) from exc
    unique_ids = list(dict.fromkeys(professional_ids))
    if not unique_ids:
        raise APIError(
            "validation_error",
            "Choisissez au moins un professionnel.",
            fields={"professional_ids": ["Obligatoire."]},
        )
    professionals = list(
        ProfessionalProfile.objects.filter(
            pk__in=unique_ids,
            is_verified=True,
            user__is_active=True,
            verification_status=ProfessionalProfile.VerificationStatus.APPROVED,
        ).select_related("user")
    )
    if len(professionals) != len(unique_ids):
        raise APIError(
            "invalid_professionals",
            "Chaque destinataire doit être un professionnel vérifié et actif.",
        )
    service_request = ServiceRequest(
        client=client,
        zone=zone,
        title=title,
        description=description,
        urgency=urgency,
        budget=budget,
        desired_date=desired_date,
        status=ServiceRequest.Status.OPEN,
    )
    service_request.save()
    for professional in professionals:
        RequestRecipient.objects.create(service_request=service_request, professional=professional)
        notify(
            recipient=professional.user,
            kind="request_received",
            title="Nouvelle demande",
            body=title,
            payload={"service_request_id": str(service_request.id)},
        )
    audit(actor=client_user, action="service_request.created", target=service_request)
    return service_request


@transaction.atomic
def update_service_request(*, service_request, client_user, changes):
    if service_request.client.user_id != client_user.id:
        raise APIError("forbidden", "Cette demande ne vous appartient pas.", status_code=403)
    if service_request.status not in (ServiceRequest.Status.OPEN, ServiceRequest.Status.QUOTED):
        raise APIError("invalid_transition", "Cette demande ne peut plus être modifiée.")
    for field in ("title", "description", "urgency", "budget", "desired_date"):
        if field in changes:
            setattr(service_request, field, changes[field])
    service_request.save()
    return service_request


@transaction.atomic
def cancel_service_request(*, service_request, client_user):
    if service_request.client.user_id != client_user.id:
        raise APIError("forbidden", "Cette demande ne vous appartient pas.", status_code=403)
    if service_request.status == ServiceRequest.Status.BOOKED:
        raise APIError("invalid_transition", "Une réservation existe déjà. Ouvrez un litige si besoin.")
    service_request.status = ServiceRequest.Status.CANCELLED
    service_request.save(update_fields=["status", "updated_at"])
    RequestRecipient.objects.filter(
        service_request=service_request,
        status=RequestRecipient.Status.PENDING,
    ).update(status=RequestRecipient.Status.REFUSED)
    audit(actor=client_user, action="service_request.cancelled", target=service_request)
    return service_request


@transaction.atomic
def decline_request(*, professional_user, service_request_id, reason=""):
    profile = professional_user.professional_profile
    try:
        recipient = RequestRecipient.objects.select_related("service_request__client__user").get(
            service_request_id=service_request_id,
            professional=profile,
        )
    except RequestRecipient.DoesNotExist as exc:
        raise APIError("forbidden", "Cette demande ne vous est pas adressée.", status_code=403) from exc
    if recipient.status in (RequestRecipient.Status.ACCEPTED, RequestRecipient.Status.REFUSED):
        raise APIError("invalid_transition", "Cette demande a déjà une réponse définitive.")
    recipient.status = RequestRecipient.Status.REFUSED
    recipient.decline_reason = reason
    recipient.save(update_fields=["status", "decline_reason", "updated_at"])
    notify(
        recipient=recipient.service_request.client.user,
        kind="request_declined",
        title="Demande refusée",
        body=profile.business_name,
        payload={"service_request_id": str(service_request_id)},
    )
    audit(actor=professional_user, action="service_request.declined", target=recipient)
    return recipient


def add_attachment(*, service_request, user, uploaded):
    if service_request.client.user_id != user.id:
        raise APIError("forbidden", "Vous ne pouvez pas joindre un fichier à cette demande.", status_code=403)
    key = store_private_file(uploaded, "requests")
    return RequestAttachment.objects.create(
        service_request=service_request,
        file_key=key,
        original_name=uploaded.name[:180],
    )


def requests_for_user(user):
    queryset = ServiceRequest.objects.select_related("client__user", "zone").prefetch_related(
        "recipients__professional"
    )
    if user.role == "client":
        return queryset.filter(client__user=user)
    if user.role == "professional":
        return queryset.filter(recipients__professional__user=user).distinct()
    if user.role == "super_admin":
        return queryset
    return queryset.none()
