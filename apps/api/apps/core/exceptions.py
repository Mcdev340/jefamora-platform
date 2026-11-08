from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class APIError(Exception):
    """Erreur métier renvoyée telle quelle au client de l'API."""

    def __init__(self, code, message, status_code=400, fields=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.fields = fields or {}


def _payload(code, message, fields=None):
    return {"code": code, "message": message, "fields": fields or {}}


def api_exception_handler(exc, context):
    if isinstance(exc, APIError):
        return Response(
            _payload(exc.code, exc.message, exc.fields),
            status=exc.status_code,
        )

    from apps.quotes.services import QuoteDecisionError

    if isinstance(exc, QuoteDecisionError):
        return Response(_payload("invalid_transition", str(exc)), status=400)

    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            fields = {key: list(value) for key, value in exc.message_dict.items()}
            message = "Les données envoyées sont invalides."
        else:
            fields = {}
            message = " ".join(exc.messages)
        return Response(_payload("validation_error", message, fields), status=400)

    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    fields = {}
    message = "Requête refusée."
    code = "error"
    if response.status_code == 429:
        code = "rate_limited"
        message = "Trop de tentatives. Réessayez dans un instant."
    elif response.status_code in (401, 403):
        code = "permission_denied"
    elif response.status_code == 404:
        code = "not_found"
        message = "Élément introuvable."
    if isinstance(data, dict):
        if "detail" in data and response.status_code not in (400,):
            message = str(data["detail"])
        elif response.status_code == 400:
            fields = {
                key: value if isinstance(value, list) else [value]
                for key, value in data.items()
                if key != "detail"
            }
            message = str(data.get("detail") or "Les données envoyées sont invalides.")
            code = "validation_error"
    response.data = _payload(code, message, fields)
    return response
