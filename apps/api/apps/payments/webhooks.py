"""Webhooks des opérateurs, inactifs en V1."""

from apps.core.exceptions import APIError


def receive(provider, payload):
    raise APIError("module_inactive", "Aucun opérateur de paiement n'est branché.", status_code=403)
