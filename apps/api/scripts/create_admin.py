"""Crée un super-administrateur. Les comptes publics ne le peuvent pas.

Usage, depuis apps/api :
    python manage.py shell < ../scripts/create_admin.py
N'imprime aucun mot de passe.
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User  # noqa: E402

email = os.environ["JEFAMORA_ADMIN_EMAIL"]
password = os.environ["JEFAMORA_ADMIN_PASSWORD"]
if User.objects.filter(email__iexact=email).exists():
    raise SystemExit("Ce compte existe déjà.")
User.objects.create_superuser(email=email, password=password)
print("Super-administrateur créé.")
