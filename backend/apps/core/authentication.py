from __future__ import annotations

from apps.core.audit_context import set_current_user
from drf_sso_resource.authentication import SSOResourceServerAuthentication


class AuditAwareSSOResourceServerAuthentication(SSOResourceServerAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, auth = result
        set_current_user(user)
        return user, auth