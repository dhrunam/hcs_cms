from .base import *

DEBUG = True

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
