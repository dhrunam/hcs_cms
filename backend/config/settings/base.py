"""
Base Django settings for HCS Case Management System.
"""
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env from the project root (backend/)
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = os.environ.get("DEBUG", "False").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Local
    "apps.accounts",
    "apps.cis",
    "apps.core",
    "apps.efiling",
    "apps.master",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASES = {
    # "default": dj_database_url.config(
    #     env="DATABASE_URL",
    #     default="postgresql://postgres:postgres@localhost:5432/hcs_cms_db",
    #     conn_max_age=600,
    #     conn_health_checks=True,
    # )

    "default": dj_database_url.config(
        env="DATABASE_URL",
        # default="postgresql://postgres:postgres@localhost:5435/hcs_cms_db",
        default=os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@10.182.144.249:5432/hcs_cms_db"),
        conn_max_age=600,
        conn_health_checks=True,
    ),

    # CIS 1.0 Legacy Database (for inspectdb introspection only)
    "cis_legacy": {
        "ENGINE": "apps.cis.db_backends.postgresql_legacy",
        "NAME": os.environ.get("CIS_LEGACY_DB_NAME", "sikkimhc_pg"),
        "USER": os.environ.get("CIS_LEGACY_DB_USER", "root"),
        "PASSWORD": os.environ.get("CIS_LEGACY_DB_PASSWORD", "ecourt"),
        "HOST": os.environ.get("CIS_LEGACY_DB_HOST", "10.182.144.249"),
        "PORT": os.environ.get("CIS_LEGACY_DB_PORT", "5432"),
        "CONN_MAX_AGE": 0,  # No connection pooling for read-only legacy DB
    },
}

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.JSONParser",
       
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# ---------------------------------------------------------------------------
# External SSO / Resource Server
# ---------------------------------------------------------------------------
SSO_BASE_URL = os.environ.get("SSO_BASE_URL", "").strip()
SSO_INTROSPECTION_URL = os.environ.get("SSO_INTROSPECTION_URL", "").strip()
SSO_CLIENT_ID = os.environ.get("SSO_CLIENT_ID", "").strip()
SSO_CLIENT_SECRET = os.environ.get("SSO_CLIENT_SECRET", "").strip()
SSO_VERIFY_SSL = os.environ.get("SSO_VERIFY_SSL", "True").lower() in ("1", "true", "yes")

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:4200").split(",")
    if o.strip()
]

CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT=BASE_DIR / "media"
MEDIA_URL = "/media/"

# ---------------------------------------------------------------------------
# Default primary key
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
