"""
Permissions
===========
DRF permission classes and utilities for OAuth2/OIDC scope- and role-based
access control.

Classes
-------
* ``HasScope`` — base class; checks ``request.token_scopes``.
* ``HasAnyScope`` — passes if the user has at least one of the required scopes.
* ``HasAllScopes`` — passes only if the user has **all** required scopes.
* ``HasSSORole`` — passes if the user belongs to a mapped Django group.
* ``AdminEditorOrReadOnly`` — backward-compatible write-guard.

Utilities
---------
* ``map_token_claims_to_groups`` — sync Django groups from OIDC role claims.
* ``ScopePermissionMapping`` — maps scopes → Django permission codenames.

Usage in views::

    class MyView(APIView):
        authentication_classes = [SSOResourceServerAuthentication]
        permission_classes = [HasAllScopes]
        required_scopes = ["cms:write"]
"""

import logging

from django.conf import settings
from django.contrib.auth.models import Group
from rest_framework import permissions

from .conf import sso_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scope-based permission classes
# ---------------------------------------------------------------------------

class IsSSOAuthenticated(permissions.BasePermission):
    """Grant access only to requests with an authenticated local user."""

    message = "Authentication credentials were not provided or are invalid."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated)

class HasScope(permissions.BasePermission):
    """
    Abstract base — subclasses must implement ``_check_scopes``.

    Views declare required_scopes as a class attribute::

        class MyView(APIView):
            permission_classes = [HasAllScopes]
            required_scopes = ["cms:write", "cms:publish"]
    """

    message = "Insufficient scope."

    def _request_scopes(self, request) -> list:
        return getattr(request, "token_scopes", [])

    def _check_scopes(self, required: list, present: list) -> bool:
        raise NotImplementedError

    def has_permission(self, request, view) -> bool:
        required = getattr(view, "required_scopes", [])
        if not required:
            return True
        present = self._request_scopes(request)
        return self._check_scopes(required, present)


class HasAnyScope(HasScope):
    """Grant access if the token contains **at least one** required scope."""

    message = "Token must include at least one of the required scopes."

    def _check_scopes(self, required, present):
        return bool(set(required) & set(present))


class HasAllScopes(HasScope):
    """Grant access only if the token contains **all** required scopes."""

    message = "Token must include all required scopes."

    def _check_scopes(self, required, present):
        return set(required).issubset(set(present))


# ---------------------------------------------------------------------------
# Role-based permission class
# ---------------------------------------------------------------------------

class HasSSORole(permissions.BasePermission):
    """
    Grant access if the user belongs to the Django group that maps from any
    of the ``required_roles`` claim values (via ``ROLE_TO_GROUP_MAP``).

    Views declare required_roles::

        class AdminView(APIView):
            permission_classes = [HasSSORole]
            required_roles = ["admin", "superuser"]
    """

    message = "Insufficient role."

    def has_permission(self, request, view) -> bool:
        required_roles = getattr(view, "required_roles", [])
        if not required_roles:
            return True

        role_map = getattr(settings, "ROLE_TO_GROUP_MAP", _default_role_mapping())
        target_groups = {
            role_map[r] for r in required_roles if r in role_map
        }
        if not target_groups:
            return False

        user = request.user
        if not user or not user.is_authenticated:
            return False

        return user.groups.filter(name__in=target_groups).exists()


# ---------------------------------------------------------------------------
# Backward-compatible write-guard
# ---------------------------------------------------------------------------

class AdminEditorOrReadOnly(permissions.BasePermission):
    """
    Read access is public (GET/HEAD/OPTIONS).
    Write access requires the user to be in ``API_WRITERS`` or ``API_ADMINS``
    groups, or have ``is_staff``/``is_superuser``.
    """

    @staticmethod
    def _normalize_iterable(value) -> set[str]:
        if value is None:
            return set()
        if isinstance(value, str):
            normalized = value.replace(",", " ")
            return {part.strip() for part in normalized.split() if part.strip()}
        if isinstance(value, (list, tuple, set)):
            return {str(part).strip() for part in value if str(part).strip()}
        return set()

    def has_permission(self, request, view) -> bool:
        safe_methods = {
            method.upper()
            for method in self._normalize_iterable(
                sso_settings.SSO_PERMISSION_SAFE_METHODS
            )
        }
        if request.method in safe_methods:
            return bool(sso_settings.SSO_PERMISSION_ALLOW_SAFE_METHODS)

        user = request.user
        if not user or not user.is_authenticated:
            return False

        if bool(sso_settings.SSO_PERMISSION_ALLOW_SUPERUSER) and user.is_superuser:
            return True
        if bool(sso_settings.SSO_PERMISSION_ALLOW_STAFF) and user.is_staff:
            return True

        role_attr = str(sso_settings.SSO_PERMISSION_USER_ROLES_ATTR)
        required_roles = self._normalize_iterable(
            sso_settings.SSO_PERMISSION_WRITE_ROLES
        )
        if required_roles:
            user_roles = self._normalize_iterable(getattr(user, role_attr, []))
            if user_roles & required_roles:
                return True

        write_groups = self._normalize_iterable(
            sso_settings.SSO_PERMISSION_WRITE_GROUPS
        )
        if not write_groups:
            return False
        return user.groups.filter(name__in=write_groups).exists()


# ---------------------------------------------------------------------------
# Scope → Django permission mapping helper
# ---------------------------------------------------------------------------

def _default_scope_mapping() -> dict:
    return {
        "api:read":  ["view_user"],
        "api:write": ["add_user", "change_user"],
        "admin":     ["delete_user"],
    }


def _default_role_mapping() -> dict:
    return {
        "admin":  "Administrators",
        "editor": "Editors",
        "viewer": "Viewers",
    }


class ScopePermissionMapping:
    """
    Maps OAuth2 scopes / OIDC roles to Django permission codenames or group
    names.  Override via ``SCOPE_TO_PERMISSION_MAP`` / ``ROLE_TO_GROUP_MAP``
    in project settings.
    """

    def __init__(self):
        self.scope_to_permission: dict = getattr(
            settings, "SCOPE_TO_PERMISSION_MAP", None
        ) or _default_scope_mapping()

        self.role_to_group: dict = getattr(
            settings, "ROLE_TO_GROUP_MAP", None
        ) or _default_role_mapping()

    def permissions_for_scope(self, scope: str) -> list:
        return self.scope_to_permission.get(scope, [])

    def group_for_role(self, role: str) -> str | None:
        return self.role_to_group.get(role)

    def permissions_for_scopes(self, scopes: list) -> set:
        result: set = set()
        for scope in scopes:
            result.update(self.permissions_for_scope(scope))
        return result


# ---------------------------------------------------------------------------
# Claims → Django groups sync
# ---------------------------------------------------------------------------

def map_token_claims_to_groups(user, claims: dict, sync: bool = True):
    """
    Sync the current user's group membership from OIDC role claims.

    ``sync=True`` removes the user from any mapped group that no longer
    appears in the token.  Groups not covered by ``ROLE_TO_GROUP_MAP`` are
    never touched.

    Returns ``(added_group_names, removed_group_names)``.
    """
    mapping = ScopePermissionMapping()

    token_roles: set = set()
    if "roles" in claims:
        raw = claims["roles"]
        token_roles = set(raw) if isinstance(raw, list) else {raw}
    elif "role" in claims:
        token_roles = {claims["role"]}
    elif "realm_access" in claims:
        token_roles = set(claims["realm_access"].get("roles", []))

    target_groups: set[str] = set()
    for role in token_roles:
        group_name = mapping.group_for_role(role)
        if group_name:
            target_groups.add(group_name)

    # Ensure all target groups exist
    groups_to_add = []
    for group_name in target_groups:
        group, created = Group.objects.get_or_create(name=group_name)
        groups_to_add.append(group)
        if created:
            logger.info("SSO: created new Django group '%s'", group_name)

    current_groups = set(user.groups.values_list("name", flat=True))

    added: list[str] = []
    for group in groups_to_add:
        if group.name not in current_groups:
            user.groups.add(group)
            added.append(group.name)

    removed: list[str] = []
    if sync:
        managed_names = set(mapping.role_to_group.values())
        for group_name in current_groups & managed_names:
            if group_name not in target_groups:
                user.groups.remove(Group.objects.get(name=group_name))
                removed.append(group_name)

    return added, removed
