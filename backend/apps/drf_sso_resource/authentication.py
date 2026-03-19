"""
SSOResourceServerAuthentication
================================
Production-ready DRF authentication backend for OAuth2/OIDC resource servers.

How it works
------------
1. Extracts the Bearer token from the ``Authorization`` header.
2. Calls the OAuth2 introspection endpoint (with retry + connection pooling).
3. Caches the result for ``SSO_INTROSPECTION_CACHE_TTL`` seconds, keyed by a
   SHA-256 digest of the token — never the raw token.
4. Falls back to ``/userinfo/`` if introspection lacks ``sub``/ username claims
   and ``SSO_ENABLE_USERINFO_FALLBACK`` is ``True``.
5. Delegates user creation / update to ``SSO_USER_SYNC_HANDLER`` so each
   project can plug in its own persistence logic without touching this file.
6. Attaches ``request.sso_claims`` for use in views and permission classes.

Extending
---------
Subclass and override ``_sync_user``, ``_resolve_identity``, or the whole
``authenticate`` if you need project-specific behaviour::

    class MyAuth(SSOResourceServerAuthentication):
        sync_handler_setting = "MY_CUSTOM_SSO_SYNC_HANDLER"
"""

import hashlib
import logging
import time

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.module_loading import import_string
from requests.adapters import HTTPAdapter
from rest_framework import authentication, exceptions
from rest_framework.permissions import SAFE_METHODS
from urllib3.util.retry import Retry

from .conf import sso_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared HTTP session (module-level singleton for connection reuse)
# ---------------------------------------------------------------------------

def _build_http_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=sso_settings.SSO_HTTP_RETRY_TOTAL,
        connect=sso_settings.SSO_HTTP_RETRY_CONNECT,
        read=sso_settings.SSO_HTTP_RETRY_READ,
        backoff_factor=sso_settings.SSO_HTTP_RETRY_BACKOFF,
        status_forcelist=(502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=sso_settings.SSO_HTTP_POOL_CONNECTIONS,
        pool_maxsize=sso_settings.SSO_HTTP_POOL_MAXSIZE,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


_HTTP_SESSION = _build_http_session()


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _token_cache_key(prefix: str, token: str) -> str:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def _ttl_from_claims(default_ttl: int, claims: dict) -> int:
    """Cap the TTL at the token's remaining lifetime if ``exp`` is present."""
    exp = claims.get("exp") if isinstance(claims, dict) else None
    if isinstance(exp, int):
        remaining = max(1, exp - int(time.time()))
        return min(default_ttl, remaining)
    return default_ttl


def _first_non_empty(claims: dict, keys: tuple):
    for key in keys:
        value = claims.get(key)
        if value:
            return value
    return None


def _fallback_username_from_sso_id(sso_id: str) -> str:
    """Build a deterministic local username when tokens don't provide one."""
    digest = hashlib.sha256(str(sso_id).encode("utf-8")).hexdigest()[:24]
    return f"sso_{digest}"


# ---------------------------------------------------------------------------
# Authentication class
# ---------------------------------------------------------------------------

class SSOResourceServerAuthentication(authentication.BaseAuthentication):
    """
    DRF authentication class for OAuth2/OIDC resource servers.

    Validate Bearer tokens via introspection, sync users via a pluggable
    handler, and attach token claims to the request for downstream use.

    Required settings
    ~~~~~~~~~~~~~~~~~
    * ``SSO_INTROSPECTION_URL``
    * ``SSO_CLIENT_ID``
    * ``SSO_CLIENT_SECRET``

    Optional extension point
    ~~~~~~~~~~~~~~~~~~~~~~~~
    * ``SSO_USER_SYNC_HANDLER`` — dotted path to
      ``callable(sso_id, username, email, claims) → User``
    """

    # Subclasses can point to a different settings key.
    sync_handler_setting: str = "SSO_USER_SYNC_HANDLER"
    default_sync_handler: str = "drf_sso_resource.user_sync.map_sso_user"

    # ------------------------------------------------------------------ #
    # Introspection                                                        #
    # ------------------------------------------------------------------ #

    def _introspect(self, token: str) -> dict | None:
        cache_key = _token_cache_key(
            sso_settings.SSO_INTROSPECTION_CACHE_PREFIX, token
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        introspect_url = sso_settings.SSO_INTROSPECTION_URL
        client_id = sso_settings.SSO_CLIENT_ID
        client_secret = sso_settings.SSO_CLIENT_SECRET

        if not (introspect_url and client_id and client_secret):
            logger.error(
                "drf_sso_resource: SSO_INTROSPECTION_URL / SSO_CLIENT_ID / "
                "SSO_CLIENT_SECRET are not fully configured."
            )
            return None

        payload = {
            "token": token,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        try:
            response = _HTTP_SESSION.post(
                introspect_url,
                data=payload,
                timeout=sso_settings.SSO_HTTP_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.warning("SSO introspection request failed: %s", exc)
            return None

        if response.status_code != 200:
            logger.warning(
                "SSO introspection non-200 status=%s", response.status_code
            )
            return None

        claims = response.json()
        if not claims.get("active"):
            return None

        ttl = _ttl_from_claims(sso_settings.SSO_INTROSPECTION_CACHE_TTL, claims)
        cache.set(cache_key, claims, ttl)
        return claims

    # ------------------------------------------------------------------ #
    # Userinfo fallback                                                    #
    # ------------------------------------------------------------------ #

    def _userinfo(self, token: str) -> dict | None:
        if not sso_settings.SSO_ENABLE_USERINFO_FALLBACK:
            return None

        cache_key = _token_cache_key(
            sso_settings.SSO_USERINFO_CACHE_PREFIX, token
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        userinfo_url = getattr(settings, "OAUTH2_USERINFO_URL", None)
        if not userinfo_url:
            base = getattr(settings, "OAUTH2_SERVER_URL", "http://localhost:8000")
            userinfo_url = f"{base}/api/oidc/userinfo/"

        try:
            response = _HTTP_SESSION.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=sso_settings.SSO_HTTP_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.warning("SSO userinfo request failed: %s", exc)
            return None

        if response.status_code != 200:
            logger.warning(
                "SSO userinfo non-200 status=%s", response.status_code
            )
            return None

        data = response.json()
        cache.set(cache_key, data, sso_settings.SSO_USERINFO_CACHE_TTL)
        return data

    # ------------------------------------------------------------------ #
    # Identity resolution                                                  #
    # ------------------------------------------------------------------ #

    def _resolve_identity(self, claims: dict) -> tuple:
        sso_id = _first_non_empty(claims, sso_settings.SSO_SUB_CLAIM_KEYS)
        username = _first_non_empty(claims, sso_settings.SSO_USERNAME_CLAIM_KEYS)
        email = _first_non_empty(claims, sso_settings.SSO_EMAIL_CLAIM_KEYS)
        return sso_id, username, email

    # ------------------------------------------------------------------ #
    # User sync                                                            #
    # ------------------------------------------------------------------ #

    def _sync_user(self, sso_id, username, email, claims):
        handler_path = getattr(
            settings, self.sync_handler_setting, self.default_sync_handler
        )
        handler = import_string(handler_path)
        return handler(sso_id, username, email, claims)

    # ------------------------------------------------------------------ #
    # DRF authenticate entry-point                                        #
    # ------------------------------------------------------------------ #

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header or auth_header[0].lower() != b"bearer":
            return None  # Not a Bearer token — let another auth class handle it

        if len(auth_header) < 2:
            return None
        if len(auth_header) > 2:
            raise exceptions.AuthenticationFailed(
                "Invalid token header — token must not contain spaces."
            )

        token = auth_header[1].decode("utf-8")

        claims = self._introspect(token)
        if not claims:
            # Public read endpoints should still work when a client sends a
            # stale/invalid bearer token; treat as anonymous for safe methods.
            if request.method in SAFE_METHODS:
                logger.warning(
                    "Bearer token could not be validated; continuing as "
                    "anonymous for safe method %s",
                    request.method,
                )
                return None

            # For non-safe methods, keep strict bearer token validation.
            raise exceptions.AuthenticationFailed(
                "Token is inactive, revoked, or the introspection endpoint is "
                "unavailable."
            )

        sso_id, username, email = self._resolve_identity(claims)

        # If introspection didn't return enough identity info, try userinfo
        if not (sso_id and username):
            userinfo = self._userinfo(token)
            if userinfo:
                claims = {**claims, **userinfo}
                sso_id, username, email = self._resolve_identity(claims)

        # Some providers only return `sub`; create a deterministic local
        # username so user provisioning/group sync can still run.
        if sso_id and not username:
            username = _fallback_username_from_sso_id(sso_id)
            logger.info(
                "Derived fallback username from sub claim for sso_id=%s", sso_id
            )

        if not sso_id:
            logger.warning(
                "SSO claims missing required identity fields "
                "(sub/username). Claims keys: %s",
                list(claims.keys()),
            )
            raise exceptions.AuthenticationFailed(
                "Token claims do not contain required subject information."
            )

        user = self._sync_user(sso_id, username, email, claims)
        if user is None:
            raise exceptions.AuthenticationFailed("User sync handler returned None.")

        # Make claims available to views and permission classes
        request.sso_claims = claims
        request.token_scopes = claims.get("scope", "").split()

        # Use a lightweight token wrapper so DRF's token auth contract is met
        class _TokenWrapper:
            def __init__(self, value):
                self.token = value

        return user, _TokenWrapper(token)

    def authenticate_header(self, request) -> str:
        return 'Bearer realm="api"'
