"""Charge un catalogue de départ si aucun métier n'existe.

À lancer depuis apps/api :
    python manage.py shell < scripts/seed_catalog.py
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.catalog.models import Category, Specialty, Trade  # noqa: E402
from apps.locations.models import Zone  # noqa: E402

CATALOG = {
    "Bâtiment": {
        "Plomberie": ["Fuite", "Installation", "Débouchage"],
        "Électricité": ["Tableau", "Prise et éclairage", "Dépannage"],
        "Maçonnerie": ["Mur", "Dalle"],
        "Peinture": ["Intérieur", "Façade"],
        "Menuiserie": ["Porte", "Fenêtre", "Placard"],
        "Carrelage": ["Sol", "Mur"],
        "Serrurerie": ["Ouverture", "Serrure"],
    },
    "Confort": {
        "Climatisation": ["Pose", "Entretien", "Recharge"],
        "Froid": ["Réfrigérateur", "Chambre froide"],
    },
    "Maison": {
        "Nettoyage": ["Appartement", "Après travaux"],
        "Jardin": ["Entretien", "Arrosage"],
    },
}

ZONES = [
    ("Dakar", "Dakar", "Plateau"),
    ("Dakar", "Dakar", "Médina"),
    ("Dakar", "Dakar", "Almadies"),
    ("Dakar", "Dakar", "Ouakam"),
    ("Dakar", "Pikine", "Pikine"),
    ("Dakar", "Guédiawaye", "Guédiawaye"),
    ("Thiès", "Thiès", "Thiès Nord"),
    ("Saint-Louis", "Saint-Louis", "Centre"),
]


def ensure_catalog():
    created = 0
    for category_name, trades in CATALOG.items():
        category, was_created = Category.objects.get_or_create(name=category_name)
        created += int(was_created)
        for trade_name, specialties in trades.items():
            trade, was_created = Trade.objects.get_or_create(category=category, name=trade_name)
            created += int(was_created)
            for specialty_name in specialties:
                _, was_created = Specialty.objects.get_or_create(trade=trade, name=specialty_name)
                created += int(was_created)
    for region, city, district in ZONES:
        _, was_created = Zone.objects.get_or_create(region=region, city=city, district=district)
        created += int(was_created)
    print(f"Catalogue prêt. {created} élément(s) ajouté(s).")


ensure_catalog()
