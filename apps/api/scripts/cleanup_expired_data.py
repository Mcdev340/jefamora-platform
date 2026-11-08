"""Marque comme consommés les codes expirés."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone  # noqa: E402

from apps.users.models import OneTimeCode  # noqa: E402

expired = OneTimeCode.objects.filter(consumed_at__isnull=True, expires_at__lt=timezone.now())
count = expired.update(consumed_at=timezone.now())
print(f"{count} code(s) expiré(s) clôturé(s).")
