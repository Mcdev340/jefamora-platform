"""Choisit le module de réglages selon DJANGO_ENV.

development par défaut. staging pour la préproduction. production pour OVH.
"""

import os

_environment = os.environ.get("DJANGO_ENV", "development").strip().lower()

if _environment == "production":
    from .production import *  # noqa: F403
elif _environment == "staging":
    from .staging import *  # noqa: F403
elif _environment == "development":
    from .development import *  # noqa: F403
else:
    raise RuntimeError("DJANGO_ENV doit valoir development, staging ou production.")
