from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def store_private_file(uploaded, folder):
    extension = Path(uploaded.name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError("Format accepté : JPG, PNG, WEBP ou PDF.")
    if uploaded.size > MAX_UPLOAD_BYTES:
        raise ValidationError("Le fichier dépasse 5 Mo.")

    relative = Path(folder) / f"{uuid4().hex}{extension}"
    destination = Path(settings.PRIVATE_MEDIA_ROOT) / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output:
        for chunk in uploaded.chunks():
            output.write(chunk)
    return relative.as_posix()


def resolve_private_file(file_key):
    root = Path(settings.PRIVATE_MEDIA_ROOT).resolve()
    path = (root / file_key).resolve()
    if root not in path.parents or not path.is_file():
        raise ValidationError("Fichier introuvable.")
    return path
