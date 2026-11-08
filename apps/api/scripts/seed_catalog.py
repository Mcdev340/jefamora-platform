"""Charge des métiers de départ si le catalogue est vide.

À lancer depuis apps/api :
    python manage.py shell < scripts/seed_catalog.py
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.catalog.models import Category, Specialty, Trade  # noqa: E402
from apps.locations.models import Zone  # noqa: E402

if Category.objects.exists():
    print("Le catalogue contient déjà des données.")
else:
    building = Category.objects.create(name="Bâtiment")
    plumbing = Trade.objects.create(category=building, name="Plomberie")
    Specialty.objects.create(trade=plumbing, name="Fuite")
    Zone.objects.create(region="Dakar", city="Dakar", district="Plateau")
    print("Catalogue initial créé.")
