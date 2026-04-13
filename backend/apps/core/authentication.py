from __future__ import annotations

from apps.core.audit_context import set_current_user
from rest_framework_simplejwt.authentication import JWTAuthentication


class AuditAwareJWTAuthentication(JWTAuthentication):
    """Validate Bearer JWTs and attach the user for audit context."""

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, auth = result
        set_current_user(user)
        return user, auth
