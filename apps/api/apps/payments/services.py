"""Fournisseurs de paiement, inactifs en V1."""

from apps.core.exceptions import APIError


def start_payment(**kwargs):
    raise APIError("module_inactive", "Le paiement intégré n'est pas activé.", status_code=403)
