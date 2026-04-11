import os

from .base import *

DEBUG = True

# Optional: same token as frontend `devAuthBypassToken` (environment.ts).
# Enables API auth in development when JWT login is not used.
_DEV_BYPASS = (os.getenv("DEV_AUTH_BYPASS_TOKEN") or "").strip()
DEV_AUTH_BYPASS_TOKEN = _DEV_BYPASS
DEV_AUTH_BYPASS_USERNAME = (os.getenv("DEV_AUTH_BYPASS_USERNAME") or "admin").strip() or "admin"

if _DEV_BYPASS:
    REST_FRAMEWORK = {
        **REST_FRAMEWORK,
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "apps.core.development_authentication.DevelopmentBypassAuthentication",
            *REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"],
        ],
    }

# Allow all CORS in development
CORS_ALLOW_ALL_ORIGINS = True

# Additional dev apps
INSTALLED_APPS += []

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
