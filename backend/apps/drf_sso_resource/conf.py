"""
Settings reference for drf-sso-resource
========================================
All settings live in the standard Django ``settings`` module and are
prefixed with ``SSO_``.  This file documents every supported key, its
type, and its default value.  Import ``sso_settings`` from here whenever
you need to read a setting inside the package so the defaults stay in one
place and are never copy-pasted.

Example project settings::

    # ── Required ──────────────────────────────────────────────────────────
    SSO_INTROSPECTION_URL = "https://sso.example.com/o/introspect/"
    SSO_CLIENT_ID         = "my-resource-server-client-id"
    SSO_CLIENT_SECRET     = "my-resource-server-client-secret"   # keep in env

    # ── User sync ─────────────────────────────────────────────────────────
    # Dotted path to a callable(sso_id, username, email, claims) → User
    SSO_USER_SYNC_HANDLER = "drf_sso_resource.user_sync.map_sso_user"

    # Swappable profile model (app_label.ModelName).
    # Override to keep using an existing profile model – no data migration needed.
    SSO_USER_PROFILE_MODEL = "drf_sso_resource.SSOUserProfile"

    # Auto-create a local user if not found (False = strict mode)
    SSO_AUTO_PROVISION_USER = False

    # ── Identity claim mapping ────────────────────────────────────────────
    SSO_SUB_CLAIM_KEYS      = ("sub", "id")
    SSO_USERNAME_CLAIM_KEYS = ("preferred_username", "username", "email")
    SSO_EMAIL_CLAIM_KEYS    = ("email",)

    # ── Userinfo fallback ─────────────────────────────────────────────────
    # When introspection response lacks sub/username, fetch /userinfo/ too
    SSO_ENABLE_USERINFO_FALLBACK = True
    OAUTH2_USERINFO_URL          = "https://sso.example.com/api/oidc/userinfo/"
    # Falls back to: {OAUTH2_SERVER_URL}/api/oidc/userinfo/

    # ── Signal-based sync ─────────────────────────────────────────────────
    # Set False to disable the app_authorized signal handler entirely
    SSO_SIGNAL_AUTO_SYNC = True

    # ── Caching ───────────────────────────────────────────────────────────
    SSO_INTROSPECTION_CACHE_PREFIX = "sso:introspection"
    SSO_INTROSPECTION_CACHE_TTL    = 120   # seconds (capped at token exp)
    SSO_USERINFO_CACHE_PREFIX      = "sso:userinfo"
    SSO_USERINFO_CACHE_TTL         = 300   # seconds

    # ── HTTP transport ────────────────────────────────────────────────────
    SSO_HTTP_TIMEOUT          = 3     # seconds per request
    SSO_HTTP_RETRY_TOTAL      = 1
    SSO_HTTP_RETRY_CONNECT    = 1
    SSO_HTTP_RETRY_READ       = 1
    SSO_HTTP_RETRY_BACKOFF    = 0.2
    SSO_HTTP_POOL_CONNECTIONS = 20
    SSO_HTTP_POOL_MAXSIZE     = 50

    # ── Group / scope mapping ─────────────────────────────────────────────
    SSO_SCOPE_GROUP_PREFIX  = "SSO_SCOPE_"           # prefix for scope-derived groups
    SSO_CLAIM_GROUP_KEYS    = ("groups", "roles")    # claim keys to read groups from
    SCOPE_TO_GROUP_MAP      = {}                      # optional scope->group mapping

    # ── DRF permission helpers ────────────────────────────────────────────
    # Mapping from OAuth2 scope to list of Django permission codenames
    SCOPE_TO_PERMISSION_MAP = {}   # overrides package default
    # Mapping from OIDC role claim value to Django group name
    ROLE_TO_GROUP_MAP       = {}   # overrides package default

    # Backward-compatible write guard configuration
    SSO_PERMISSION_ALLOW_SAFE_METHODS = True
    SSO_PERMISSION_SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
    SSO_PERMISSION_WRITE_GROUPS = ("API_WRITERS", "API_ADMINS")
    SSO_PERMISSION_WRITE_ROLES = ("admin", "editor")
    SSO_PERMISSION_USER_ROLES_ATTR = "roles"
    SSO_PERMISSION_ALLOW_STAFF = True
    SSO_PERMISSION_ALLOW_SUPERUSER = True
"""

from django.conf import settings as _django_settings


# ---------------------------------------------------------------------------
# Internal defaults dict — single source of truth
# ---------------------------------------------------------------------------
_DEFAULTS: dict = {
    # Required (no sensible defaults – must be set by the project)
    "SSO_INTROSPECTION_URL": None,
    "SSO_CLIENT_ID": None,
    "SSO_CLIENT_SECRET": None,
    # User sync
    "SSO_USER_SYNC_HANDLER": "drf_sso_resource.user_sync.map_sso_user",
    "SSO_USER_PROFILE_MODEL": "drf_sso_resource.SSOUserProfile",
    "SSO_AUTO_PROVISION_USER": False,
    # Identity claim keys
    "SSO_SUB_CLAIM_KEYS": ("sub", "id"),
    "SSO_USERNAME_CLAIM_KEYS": ("preferred_username", "username", "email"),
    "SSO_EMAIL_CLAIM_KEYS": ("email",),
    # Userinfo fallback
    "SSO_ENABLE_USERINFO_FALLBACK": True,
    # Signal
    "SSO_SIGNAL_AUTO_SYNC": True,
    # Cache
    "SSO_INTROSPECTION_CACHE_PREFIX": "sso:introspection",
    "SSO_INTROSPECTION_CACHE_TTL": 120,
    "SSO_USERINFO_CACHE_PREFIX": "sso:userinfo",
    "SSO_USERINFO_CACHE_TTL": 300,
    # HTTP transport
    "SSO_HTTP_TIMEOUT": 3,
    "SSO_HTTP_RETRY_TOTAL": 1,
    "SSO_HTTP_RETRY_CONNECT": 1,
    "SSO_HTTP_RETRY_READ": 1,
    "SSO_HTTP_RETRY_BACKOFF": 0.2,
    "SSO_HTTP_POOL_CONNECTIONS": 20,
    "SSO_HTTP_POOL_MAXSIZE": 50,
    # Groups
    "SSO_SCOPE_GROUP_PREFIX": "SSO_SCOPE_",
    "SSO_CLAIM_GROUP_KEYS": ("groups", "roles"),
    "SCOPE_TO_GROUP_MAP": None,  # None = no explicit scope->group mapping
    # Permission maps
    "SCOPE_TO_PERMISSION_MAP": None,  # None = use package default
    "ROLE_TO_GROUP_MAP": None,        # None = use package default
    # Backward-compatible write guard
    "SSO_PERMISSION_ALLOW_SAFE_METHODS": True,
    "SSO_PERMISSION_SAFE_METHODS": ("GET", "HEAD", "OPTIONS"),
    "SSO_PERMISSION_WRITE_GROUPS": ("API_WRITERS", "API_ADMINS", "API_READERS"),
    "SSO_PERMISSION_WRITE_ROLES": ("admin", "editor"),
    "SSO_PERMISSION_USER_ROLES_ATTR": "roles",
    "SSO_PERMISSION_ALLOW_STAFF": True,
    "SSO_PERMISSION_ALLOW_SUPERUSER": True,
}


class _SSOSettings:
    """Thin wrapper that reads from Django settings with package defaults."""

    def __getattr__(self, name: str):
        if name not in _DEFAULTS:
            raise AttributeError(f"Unknown SSO setting: {name!r}")
        return getattr(_django_settings, name, _DEFAULTS[name])

    def require(self, *names: str) -> None:
        """Raise SSOConfigError if any of the given settings are None/empty."""
        from .exceptions import SSOConfigError

        missing = [n for n in names if not getattr(self, n)]
        if missing:
            raise SSOConfigError(
                f"The following required SSO settings are not configured: "
                f"{', '.join(missing)}"
            )


sso_settings = _SSOSettings()
