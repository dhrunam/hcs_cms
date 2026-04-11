"""
Optional local-dev auth: accepts a fixed Bearer token when DEBUG and
DEV_AUTH_BYPASS_TOKEN are set (e.g. quick testing without JWT login).

Never enable DEV_AUTH_BYPASS_TOKEN in production.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication

from apps.core.audit_context import set_current_user

logger = logging.getLogger(__name__)


class DevelopmentBypassAuthentication(authentication.BaseAuthentication):
    """Authenticate as a configured Django user when Bearer matches dev token."""

    def authenticate(self, request):
        expected = getattr(settings, "DEV_AUTH_BYPASS_TOKEN", "") or ""
        if not settings.DEBUG or not (expected and str(expected).strip()):
            return None

        auth_header = authentication.get_authorization_header(request).split()
        if not auth_header or auth_header[0].lower() != b"bearer":
            return None
        if len(auth_header) != 2:
            return None

        token = auth_header[1].decode("utf-8")
        if token != str(expected).strip():
            return None

        User = get_user_model()
        username = getattr(settings, "DEV_AUTH_BYPASS_USERNAME", "") or "admin"
        username = str(username).strip() or "admin"
        user = User.objects.filter(username__iexact=username).first()
        if user is None:
            user = User.objects.filter(is_superuser=True).first()
        if user is None:
            logger.warning(
                "DEV_AUTH_BYPASS_TOKEN is set but no user matched username=%r and no superuser exists.",
                username,
            )
            return None

        set_current_user(user)
        return user, None
