"""
Base Django settings for HCS Case Management System.
"""
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def env_list(name, default=""):
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]

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
    "apps.payment",
    "apps.listing",
    "apps.judge",
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
        default=os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hcs_cms_db"),
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
    "DEFAULT_PERMISSION_CLASSES": [],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.JSONParser",
       
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "config.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
}

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

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# ---------------------------------------------------------------------------
# Default primary key
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# E-filing PDF validation (size <= 25 MB, OCR/text layer required)
# ---------------------------------------------------------------------------
EFILING_VALIDATE_PDF_UPLOAD = True



# OAUTH2_SERVER_URL = os.getenv('OAUTH2_SERVER_URL', 'http://localhost:8000')
# OAUTH2_USERINFO_URL = os.getenv('OAUTH2_USERINFO_URL', f'{OAUTH2_SERVER_URL}/api/oidc/userinfo/')
# SSO_BASE_URL = os.getenv('SSO_BASE_URL', OAUTH2_SERVER_URL).strip()
# SSO_INTROSPECTION_URL = os.getenv('SSO_INTROSPECTION_URL', 'http://localhost:8000/o/introspect/')
# SSO_CLIENT_ID = os.getenv('SSO_CLIENT_ID', '')
# SSO_CLIENT_SECRET = os.getenv('SSO_CLIENT_SECRET', '')
# SSO_VERIFY_SSL = env_bool('SSO_VERIFY_SSL', True)
# SSO_HTTP_TIMEOUT = float(os.getenv('SSO_HTTP_TIMEOUT', '3'))
# SSO_HTTP_RETRY_TOTAL = int(os.getenv('SSO_HTTP_RETRY_TOTAL', '1'))
# SSO_HTTP_RETRY_CONNECT = int(os.getenv('SSO_HTTP_RETRY_CONNECT', '1'))
# SSO_HTTP_RETRY_READ = int(os.getenv('SSO_HTTP_RETRY_READ', '1'))
# SSO_HTTP_RETRY_BACKOFF = float(os.getenv('SSO_HTTP_RETRY_BACKOFF', '0.2'))
# SSO_HTTP_POOL_CONNECTIONS = int(os.getenv('SSO_HTTP_POOL_CONNECTIONS', '20'))
# SSO_HTTP_POOL_MAXSIZE = int(os.getenv('SSO_HTTP_POOL_MAXSIZE', '50'))
# SSO_INTROSPECTION_CACHE_TTL = int(os.getenv('SSO_INTROSPECTION_CACHE_TTL', '120'))
# SSO_USERINFO_CACHE_TTL = int(os.getenv('SSO_USERINFO_CACHE_TTL', '300'))
# SSO_INTROSPECTION_CACHE_PREFIX = os.getenv('SSO_INTROSPECTION_CACHE_PREFIX', 'sso:introspection')
# SSO_USERINFO_CACHE_PREFIX = os.getenv('SSO_USERINFO_CACHE_PREFIX', 'sso:userinfo')
# SSO_ENABLE_USERINFO_FALLBACK = env_bool('SSO_ENABLE_USERINFO_FALLBACK', True)
# SSO_USER_SYNC_HANDLER = os.getenv('SSO_USER_SYNC_HANDLER', 'drf_sso_resource.user_sync.map_sso_user')

# The package registers the app_authorized signal automatically.
# Set False here only if you want to disable signal-based sync entirely.
# SSO_SIGNAL_AUTO_SYNC = env_bool('SSO_SIGNAL_AUTO_SYNC', True)
# SSO_SUB_CLAIM_KEYS = tuple(env_list('SSO_SUB_CLAIM_KEYS', 'sub,id'))
# SSO_USERNAME_CLAIM_KEYS = tuple(env_list('SSO_USERNAME_CLAIM_KEYS', 'preferred_username,username,email'))
# SSO_EMAIL_CLAIM_KEYS = tuple(env_list('SSO_EMAIL_CLAIM_KEYS', 'email'))

# ---------------------------------------------------------------------------
# Payment Gateway (SBS UAT)
# ---------------------------------------------------------------------------
PG_PARAMS = {
    "merchant_code": os.getenv("PG_MERCHANT_CODE", "sikkimnic_sbs_uat_2021"),
    "major_head_code": os.getenv("PG_MAJOR_HEAD_CODE", "0215"),
    "minor_head_code": os.getenv("PG_MINOR_HEAD_CODE", "01.103"),
    "return_url": os.getenv("PG_RETURN_URL", "http://localhost:8002/api/payment/response"),
    "redirect_to_front_end_for_application_fee_paymet_status_page": os.getenv(
        "PG_APPLICATION_REDIRECT_URL",
        "http://localhost:4200/advocate/dashboard/efiling/new-filing",
    ),
    "redirect_to_front_end_for_application_fee_paymet_status_page_draft": os.getenv(
        "PG_APPLICATION_DRAFT_REDIRECT_URL",
        "http://localhost:4200/advocate/dashboard/efiling/draft-filings/edit",
    ),
    "redirect_to_front_end_for_intimation_fee_paymet_status_page": os.getenv(
        "PG_INTIMATION_REDIRECT_URL",
        "http://localhost:4200/dashboard/payment?application=",
    ),
    "salt": os.getenv(
        "PG_SALT",
        "31c6163218e5c8233ea9af089785bd3125b210cc995add2da23e36d0779d51d7",
    ),
    "payment_request_url": os.getenv(
        "PG_PAYMENT_REQUEST_URL",
        "https://www.sbsebr.com/sbsuat/UATInitiateTransaction/PaymentRequestGOS",
    ),
    "payment_status_url": os.getenv(
        "PG_PAYMENT_STATUS_URL",
        "https://www.sbsebr.com/sbsuat/UATInitiateTransaction/GetTransactionStatus",
    ),
}

PG_PAYMENT_STATUS = {
    "initiated": "initiated",
    "success": "success",
    "failed": "failed",
}