"""
Signal handlers
===============
Connects to ``oauth2_provider.signals.app_authorized`` to sync SSO user data
whenever a new token is issued — useful for server-to-server flows where the
token is used immediately after being issued.

Auto-wired in ``DRFSSOResourceConfig.ready()`` when
``SSO_SIGNAL_AUTO_SYNC = True`` (the default).

Set ``SSO_SIGNAL_AUTO_SYNC = False`` in your project settings to opt out
(e.g. if you rely solely on per-request sync via the authentication class).
"""

import logging

import requests
from django.conf import settings
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# Guard: only connect when SSO_SIGNAL_AUTO_SYNC is enabled.
_auto_sync = getattr(settings, "SSO_SIGNAL_AUTO_SYNC", True)

if _auto_sync:
    try:
        from oauth2_provider.signals import app_authorized

        @receiver(app_authorized)
        def _sync_user_on_token_authorized(sender, request, token, **kwargs):
            """
            Fetch userinfo from the SSO provider and sync the user record
            immediately after a token is issued.
            """
            from django.utils.module_loading import import_string
            from .conf import sso_settings

            userinfo_url = getattr(settings, "OAUTH2_USERINFO_URL", None)
            if not userinfo_url:
                base = getattr(
                    settings, "OAUTH2_SERVER_URL", "http://localhost:8000"
                )
                userinfo_url = f"{base}/api/oidc/userinfo/"

            try:
                resp = requests.get(
                    userinfo_url,
                    headers={"Authorization": f"Bearer {token.token}"},
                    timeout=sso_settings.SSO_HTTP_TIMEOUT,
                )
            except requests.RequestException as exc:
                logger.warning(
                    "SSO signal: userinfo request failed: %s", exc
                )
                return

            if resp.status_code != 200:
                logger.warning(
                    "SSO signal: userinfo returned status=%s", resp.status_code
                )
                return

            data = resp.json()
            sub_keys = sso_settings.SSO_SUB_CLAIM_KEYS
            username_keys = sso_settings.SSO_USERNAME_CLAIM_KEYS
            email_keys = sso_settings.SSO_EMAIL_CLAIM_KEYS

            sso_id = next((data.get(k) for k in sub_keys if data.get(k)), None)
            username = next(
                (data.get(k) for k in username_keys if data.get(k)), None
            )
            email = next((data.get(k) for k in email_keys if data.get(k)), None)

            if not (sso_id and username):
                logger.warning(
                    "SSO signal: userinfo missing sub/username. Keys: %s",
                    list(data.keys()),
                )
                return

            handler_path = getattr(
                settings,
                "SSO_USER_SYNC_HANDLER",
                "drf_sso_resource.user_sync.map_sso_user",
            )
            try:
                handler = import_string(handler_path)
                handler(sso_id, username, email, data)
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "SSO signal: user sync handler raised an exception: %s", exc
                )

    except ImportError:
        logger.debug(
            "django-oauth-toolkit not installed; "
            "SSO app_authorized signal not connected."
        )
