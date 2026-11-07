"""Choisit le module de réglages selon DJANGO_ENV.

development par défaut. En production : DJANGO_ENV=production.
"""

import os

_environment = os.environ.get("DJANGO_ENV", "development").strip().lower()

if _environment == "production":
    from .production import *  # noqa: F403
elif _environment == "development":
    from .development import *  # noqa: F403
else:
    raise RuntimeError("DJANGO_ENV doit valoir development ou production.")
