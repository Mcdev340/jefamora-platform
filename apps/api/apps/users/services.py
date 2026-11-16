import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.audit.services import audit, security_event
from apps.clients.models import ClientProfile
from apps.core.exceptions import APIError
from apps.core.request import client_ip
from apps.users.models import DeviceSession, OneTimeCode, User
from apps.users.tokens import JefamoraRefreshToken
from apps.privacy.models import UserConsent
from apps.catalog.models import Trade
from apps.locations.models import Zone
from apps.professionals.models import ProfessionalProfile, ProfessionalService


def _send_code_mail(user, purpose, code):
    if purpose == OneTimeCode.Purpose.EMAIL_VERIFICATION:
        subject = "Confirmez votre adresse Jefamora"
        intro = "Votre code de vérification Jefamora :"
    else:
        subject = "Réinitialisation de votre mot de passe Jefamora"
        intro = "Votre code de réinitialisation Jefamora :"
    send_mail(
        subject,
        f"Bonjour,\n\n{intro} {code}\nIl expire dans 30 minutes.\n",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def issue_code(user, purpose):
    code = f"{secrets.randbelow(1_000_000):06d}"
    token = secrets.token_urlsafe(32)
    OneTimeCode.objects.filter(
        user=user,
        purpose=purpose,
        consumed_at__isnull=True,
    ).update(consumed_at=timezone.now())
    OneTimeCode.objects.create(
        user=user,
        purpose=purpose,
        code_hash=make_password(code),
        token_hash=make_password(token),
        expires_at=timezone.now() + timedelta(minutes=30),
    )
    transaction.on_commit(lambda: _send_code_mail(user, purpose, code))
    return code


def _consume_code(user, purpose, code=None, token=None):
    records = OneTimeCode.objects.filter(
        user=user,
        purpose=purpose,
        consumed_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).order_by("-created_at")[:5]
    for record in records:
        matched = (code and check_password(code, record.code_hash)) or (
            token and record.token_hash and check_password(token, record.token_hash)
        )
        if matched:
            record.consumed_at = timezone.now()
            record.save(update_fields=["consumed_at"])
            return record
    raise APIError("invalid_code", "Code invalide ou expiré.", status_code=400)


def issue_session(user, request):
    refresh = JefamoraRefreshToken.for_user(user)
    DeviceSession.objects.create(
        user=user,
        refresh_jti=str(refresh["jti"]),
        user_agent=(request.META.get("HTTP_USER_AGENT", "") if request else "")[:255],
        ip_address=client_ip(request),
    )
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


def profile_payload(user):
    payload = {
        "id": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_verified": user.is_verified,
    }
    try:
        client = user.client_profile
    except ObjectDoesNotExist:
        client = None
    if client is not None:
        payload["client_profile_id"] = str(client.id)
        payload["company_name"] = client.company_name
    try:
        professional = user.professional_profile
    except ObjectDoesNotExist:
        professional = None
    if professional is not None:
        payload["professional_profile_id"] = str(professional.id)
        payload["business_name"] = professional.business_name
        payload["badge_verified"] = professional.is_verified
        payload["verification_status"] = professional.verification_status
    return payload


@transaction.atomic
def register_account(*, data, request):
    role = data["role"]
    if role not in (User.Role.CLIENT, User.Role.PROFESSIONAL):
        raise APIError("invalid_role", "Choisissez un compte client ou professionnel.")
    if not data.get("accept_terms"):
        raise APIError(
            "consent_required",
            "L'acceptation des conditions est obligatoire.",
            fields={"accept_terms": ["Obligatoire."]},
        )
    business_name = (data.get("business_name") or "").strip()
    if role == User.Role.PROFESSIONAL and not business_name:
        raise APIError(
            "validation_error",
            "Le nom professionnel est obligatoire.",
            fields={"business_name": ["Obligatoire."]},
        )
    try:
        validate_password(data["password"])
    except ValidationError as exc:
        raise APIError(
            "validation_error",
            "Mot de passe trop faible.",
            fields={"password": list(exc.messages)},
        ) from exc
    try:
        user = User.objects.create_user(
            email=data["email"],
            password=data["password"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            phone=data.get("phone") or None,
            role=role,
            is_verified=False,
        )
    except IntegrityError as exc:
        raise APIError(
            "already_exists",
            "Un compte existe déjà avec cet e-mail ou ce téléphone.",
            status_code=409,
        ) from exc
    if role == User.Role.CLIENT:
        ClientProfile.objects.create(user=user, company_name=data.get("company_name", ""))
    else:
        profile = ProfessionalProfile.objects.create(user=user, business_name=business_name)
        trade_id = data.get("trade_id")
        trade_name = (data.get("trade") or "").strip()
        if trade_id or trade_name:
            trade = None
            if trade_id:
                trade = Trade.objects.filter(id=trade_id, is_active=True).first()
            if trade is None and trade_name:
                trade = Trade.objects.filter(name__iexact=trade_name, is_active=True).first()
            if trade is None:
                raise APIError(
                    "validation_error",
                    "Choisissez un métier du catalogue.",
                    fields={"trade": ["Métier inconnu ou inactif."]},
                )
            ProfessionalService.objects.create(profile=profile, trade=trade, title=trade.name)
        city = (data.get("city") or "").strip()
        if city:
            zones = list(Zone.objects.filter(region__iexact="Dakar", city__iexact=city, is_active=True))
            if not zones:
                raise APIError(
                    "validation_error",
                    "Choisissez une ville du référentiel.",
                    fields={"city": ["Ville inconnue ou inactive."]},
                )
            profile.assign_zones(zones)
    UserConsent.objects.create(user=user, code="terms", version="v1", granted=True)
    issue_code(user, OneTimeCode.Purpose.EMAIL_VERIFICATION)
    audit(actor=user, action="account.registered", target=user, request=request)
    return user


@transaction.atomic
def verify_email(*, email, code=None, token=None, request=None):
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        raise APIError("invalid_code", "Code invalide ou expiré.")
    _consume_code(user, OneTimeCode.Purpose.EMAIL_VERIFICATION, code=code, token=token)
    user.is_verified = True
    user.save(update_fields=["is_verified", "updated_at"])
    audit(actor=user, action="account.email_verified", target=user, request=request)
    tokens = issue_session(user, request)
    return user, tokens


def login_account(*, email, password, request):
    user = authenticate(request, username=email, password=password)
    if user is None:
        security_event(kind="login_failed", request=request, detail=email[:255])
        raise APIError("invalid_credentials", "E-mail ou mot de passe incorrect.", status_code=401)
    if not user.is_active:
        raise APIError("inactive", "Ce compte est suspendu.", status_code=403)
    if not user.is_verified:
        raise APIError(
            "email_unverified",
            "Confirmez votre adresse e-mail avant de vous connecter.",
            status_code=403,
        )
    audit(actor=user, action="account.login", target=user, request=request)
    return user, issue_session(user, request)


def logout_account(*, refresh, request):
    try:
        token = JefamoraRefreshToken(refresh)
        token.blacklist()
    except TokenError as exc:
        raise APIError("invalid_token", "Session déjà close ou jeton invalide.", status_code=401) from exc
    DeviceSession.objects.filter(refresh_jti=str(token["jti"])).update(revoked_at=timezone.now())
    user = User.objects.filter(pk=token["user_id"]).first()
    if user is not None:
        audit(actor=user, action="account.logout", target=user, request=request)


def refresh_session(*, refresh):
    try:
        token = JefamoraRefreshToken(refresh)
        token.blacklist()
        user = User.objects.get(pk=token["user_id"])
    except (TokenError, User.DoesNotExist) as exc:
        raise APIError("invalid_token", "Jeton de rafraîchissement invalide.", status_code=401) from exc
    if not user.is_active:
        raise APIError("inactive", "Ce compte est suspendu.", status_code=403)
    DeviceSession.objects.filter(refresh_jti=str(token["jti"])).update(revoked_at=timezone.now())
    rotated = JefamoraRefreshToken.for_user(user)
    DeviceSession.objects.create(user=user, refresh_jti=str(rotated["jti"]))
    return {"access": str(rotated.access_token), "refresh": str(rotated)}


def request_password_reset(*, email):
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if user is not None:
        issue_code(user, OneTimeCode.Purpose.PASSWORD_RESET)


@transaction.atomic
def confirm_password_reset(*, email, code, password):
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        raise APIError("invalid_code", "Code invalide ou expiré.")
    try:
        validate_password(password, user)
    except ValidationError as exc:
        raise APIError(
            "validation_error",
            "Mot de passe trop faible.",
            fields={"password": list(exc.messages)},
        ) from exc
    _consume_code(user, OneTimeCode.Purpose.PASSWORD_RESET, code=code)
    user.set_password(password)
    user.save(update_fields=["password", "updated_at"])
    for outstanding in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=outstanding)
    DeviceSession.objects.filter(user=user, revoked_at__isnull=True).update(revoked_at=timezone.now())
    audit(actor=user, action="account.password_reset", target=user)


def revoke_session(*, user, session_id):
    updated = DeviceSession.objects.filter(user=user, pk=session_id, revoked_at__isnull=True).update(
        revoked_at=timezone.now()
    )
    if not updated:
        raise APIError("not_found", "Session introuvable.", status_code=404)
    outstanding = OutstandingToken.objects.filter(user=user, jti=DeviceSession.objects.get(pk=session_id).refresh_jti).first()
    if outstanding is not None:
        BlacklistedToken.objects.get_or_create(token=outstanding)
