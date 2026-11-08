"""Réglages communs à tous les environnements."""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent.parent

env = environ.Env(DJANGO_DEBUG=(bool, False))
environ.Env.read_env(PROJECT_ROOT / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_filters",
    "apps.core",
    "apps.users",
    "apps.catalog",
    "apps.locations",
    "apps.clients",
    "apps.favorites",
    "apps.professionals",
    "apps.verification",
    "apps.portfolio",
    "apps.service_requests",
    "apps.quotes",
    "apps.bookings",
    "apps.messaging",
    "apps.reviews",
    "apps.moderation",
    "apps.support",
    "apps.notifications",
    "apps.audit",
    "apps.analytics",
    "apps.privacy",
    "apps.administration",
    "apps.payments",
    "apps.subscriptions",
    "apps.ai_assistant",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env.int("POSTGRES_PORT", default=5432),
        "CONN_MAX_AGE": env.int("POSTGRES_CONN_MAX_AGE", default=60),
        "CONN_HEALTH_CHECKS": True,
        "TEST": {
            "NAME": env("POSTGRES_TEST_DB", default="jefamora_test"),
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Dakar"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = PROJECT_ROOT / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_ROOT / "media"
PRIVATE_MEDIA_ROOT = PROJECT_ROOT / "private_media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "identity.User"

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Jefamora <noreply@localhost>")
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:4200")

DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "apps.core.schema.AppTagAutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "apps.core.permissions.IsEmailVerified",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.DefaultPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "120/minute",
        "anon": "30/minute",
        "auth": "10/minute",
    },
    "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_MINUTES", default=15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Jefamora API",
    "DESCRIPTION": "API de la plateforme Jefamora. Chaque groupe porte le nom de l'app, puis ses routes.",
    "VERSION": "v1",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {"name": "core", "description": "Santé de l'API."},
        {"name": "users", "description": "Compte, connexion et profil."},
        {"name": "locations", "description": "Zones et adresses."},
        {"name": "favorites", "description": "Professionnels mis de côté."},
        {"name": "clients", "description": "Profil client."},
        {"name": "catalog", "description": "Catégories, métiers et spécialités."},
        {"name": "professionals", "description": "Profil, services, zones et recherche."},
        {"name": "portfolio", "description": "Réalisations."},
        {"name": "service_requests", "description": "Demandes de service."},
        {"name": "quotes", "description": "Devis."},
        {"name": "bookings", "description": "Missions."},
        {"name": "messaging", "description": "Messages de la mission."},
        {"name": "reviews", "description": "Avis."},
        {"name": "moderation", "description": "Signalements et blocages."},
        {"name": "notifications", "description": "Notifications."},
        {"name": "verification", "description": "Badge Profil vérifié."},
        {"name": "support", "description": "Tickets et preuves de litige."},
        {"name": "privacy", "description": "Données personnelles."},
        {"name": "payments", "description": "Paiement, inactif en V1."},
        {"name": "subscriptions", "description": "Abonnements, inactifs en V1."},
        {"name": "ai_assistant", "description": "Assistant, inactif en V1."},
        {"name": "audit", "description": "Journal des actions sensibles."},
        {"name": "analytics", "description": "Statistiques et exports."},
        {"name": "administration", "description": "Back-office super-admin."},
    ],
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
