from django.urls import path

from apps.users.api.v1.views import (
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RefreshView,
    RegisterView,
    SessionListView,
    SessionRevokeView,
    VerifyEmailView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("verify-email/", VerifyEmailView.as_view(), name="auth-verify-email"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="auth-password-reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-confirm"),
    path("sessions/", SessionListView.as_view(), name="auth-sessions"),
    path("sessions/<uuid:session_id>/", SessionRevokeView.as_view(), name="auth-session-revoke"),
    path("me/", MeView.as_view(), name="me"),
]
