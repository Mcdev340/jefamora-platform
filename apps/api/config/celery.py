"""Point d'entrée Celery, branché quand Redis est disponible.

Le processus web n'importe pas ce module. Les notifications restent
enregistrées dans l'application tant que le worker n'est pas lancé.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_ENV", "development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("jefamora")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
