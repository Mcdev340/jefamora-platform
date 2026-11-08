from pathlib import Path

from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def validate_private_upload(uploaded):
    extension = Path(uploaded.name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError("Format accepté : JPG, PNG, WEBP ou PDF.")
    if uploaded.size > MAX_UPLOAD_BYTES:
        raise ValidationError("Le fichier dépasse 5 Mo.")
    return extension
