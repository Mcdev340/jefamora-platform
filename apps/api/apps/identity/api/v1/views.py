from django.db import IntegrityError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.core.exceptions import APIError
from apps.core.permissions import IsEmailVerified
from apps.identity.api.v1.serializers import (
    LoginSerializer,
    MeUpdateSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RefreshSerializer,
    RegisterSerializer,
    VerifyEmailSerializer,
)
from apps.identity.models import DeviceSession
from apps.identity.services.accounts import (
    confirm_password_reset,
    login_account,
    logout_account,
    profile_payload,
    refresh_session,
    register_account,
    request_password_reset,
    revoke_session,
    verify_email,
)


class AuthRateThrottle(AnonRateThrottle):
    scope = "auth"


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_account(data=serializer.validated_data, request=request)
        return Response(
            {"email": user.email, "message": "Un code de vérification a été envoyé."},
            status=201,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, tokens = verify_email(request=request, **serializer.validated_data)
        return Response({**tokens, "profile": profile_payload(user)})


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, tokens = login_account(request=request, **serializer.validated_data)
        return Response({**tokens, "profile": profile_payload(user)})


class RefreshView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = RefreshSerializer

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(refresh_session(refresh=serializer.validated_data["refresh"]))


class LogoutView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RefreshSerializer

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logout_account(refresh=serializer.validated_data["refresh"], request=request)
        return Response(status=204)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_password_reset(email=serializer.validated_data["email"])
        return Response({"message": "Si ce compte existe, un code a été envoyé."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirm_password_reset(**serializer.validated_data)
        return Response({"message": "Mot de passe mis à jour."})


class SessionListView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        sessions = DeviceSession.objects.filter(user=request.user)
        return Response(
            [
                {
                    "id": str(item.id),
                    "user_agent": item.user_agent,
                    "ip_address": item.ip_address,
                    "revoked_at": item.revoked_at,
                    "created_at": item.created_at,
                }
                for item in sessions
            ]
        )


class SessionRevokeView(APIView):
    permission_classes = [IsEmailVerified]

    def delete(self, request, session_id):
        revoke_session(user=request.user, session_id=session_id)
        return Response(status=204)


class MeView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        return Response(profile_payload(request.user))

    def patch(self, request):
        serializer = MeUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = request.user
        data = serializer.validated_data
        for field in ("first_name", "last_name"):
            if field in data:
                setattr(user, field, data[field])
        if "phone" in data:
            user.phone = data["phone"] or None
        try:
            user.save()
        except IntegrityError as exc:
            raise APIError("already_exists", "Ce téléphone est déjà utilisé.", status_code=409) from exc
        if "company_name" in data and user.role == "client":
            profile = user.client_profile
            profile.company_name = data["company_name"]
            profile.save(update_fields=["company_name", "updated_at"])
        return Response(profile_payload(user))
