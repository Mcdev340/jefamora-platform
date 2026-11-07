from rest_framework.permissions import BasePermission

from apps.identity.models import User


class IsEmailVerified(BasePermission):
    """L'accès à la plateforme commence après la confirmation de l'e-mail."""

    message = "Confirmez votre adresse e-mail avant de continuer."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.is_verified
        )


class IsClient(IsEmailVerified):
    message = "Cette action est réservée à un client."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == User.Role.CLIENT


class IsProfessional(IsEmailVerified):
    message = "Cette action est réservée à un professionnel."

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.role == User.Role.PROFESSIONAL
        )


class IsSuperAdmin(BasePermission):
    message = "Cette action est réservée à un super-administrateur."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.is_staff
            and user.role == User.Role.SUPER_ADMIN
        )
