"""Abonnements professionnels, inactifs en V1."""

from apps.core.exceptions import APIError


def subscribe(**kwargs):
    raise APIError("module_inactive", "Les abonnements ne sont pas activés.", status_code=403)
