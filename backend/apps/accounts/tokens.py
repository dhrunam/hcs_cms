"""Custom JWT access/refresh tokens with role/group claims for Angular clients."""

from __future__ import annotations

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.accounts import roles as role_defs


def primary_role_key_for_user(user) -> str:
    """First matching app role key from the user's Django groups (stable order)."""
    names = set(user.groups.values_list("name", flat=True))
    for key in role_defs.ALL_ROLE_KEYS:
        group_name = role_defs.ROLE_TO_GROUP_MAP.get(key)
        if group_name and group_name in names:
            return key
    return ""


class HCSAccessToken(AccessToken):
    """Access token including `role` and `groups` for the SPA."""

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        groups = list(user.groups.order_by("name").values_list("name", flat=True))
        token["groups"] = groups
        token["role"] = primary_role_key_for_user(user)
        return token


class HCSRefreshToken(RefreshToken):
    """Refresh token whose `.access_token` uses `HCSAccessToken` (claims preserved on refresh)."""

    access_token_class = HCSAccessToken
