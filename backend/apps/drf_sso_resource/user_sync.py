"""
User sync utilities
===================
Low-level helpers for upserting Django users and syncing group membership
from OIDC/OAuth2 token claims.

These functions contain no project-specific imports and work with any
``AUTH_USER_MODEL``.

Default sync handler
--------------------
``map_sso_user`` is the default value of ``SSO_USER_SYNC_HANDLER``. It:

* Upserts the Django user by username.
* Creates / updates an ``SSOUserProfile`` (model selected via
  ``SSO_USER_PROFILE_MODEL``) to store the raw claims.
* Syncs Django group membership from OIDC claim groups/roles.
* Maps OAuth2 scopes to ``SSO_SCOPE_<SCOPE>`` groups.

Override ``SSO_USER_SYNC_HANDLER`` in your project settings to replace this
with any ``callable(sso_id, username, email, claims) -> User``.
"""

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .conf import sso_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Low-level user / group helpers (reusable building blocks)
# ---------------------------------------------------------------------------

def upsert_user_by_username(username: str, email: str | None = None):
    """
    Get-or-create a User by username; update email if it changed.

    Returns ``(user, created)``.
    """
    UserModel = get_user_model()
    user, created = UserModel.objects.get_or_create(
        username=username,
        defaults={"email": email or ""},
    )
    if not created and email and user.email != email:
        user.email = email
        user.save(update_fields=["email"])
    return user, created


def ensure_groups(group_names: set) -> dict:
    """
    Bulk get-or-create Django groups by name.

    Returns a ``{name: Group}`` dict for *all* requested names.
    """
    group_names = set(group_names)
    if not group_names:
        return {}

    existing = {g.name: g for g in Group.objects.filter(name__in=group_names)}
    missing = group_names - set(existing.keys())
    if missing:
        Group.objects.bulk_create(
            [Group(name=name) for name in missing], ignore_conflicts=True
        )
        existing = {g.name: g for g in Group.objects.filter(name__in=group_names)}
    return existing


def sync_groups(user, target_group_names, managed_group_names=None) -> None:
    """
    Bring ``user``'s membership in *managed* groups in line with
    ``target_group_names``.

    ``managed_group_names`` defines the set of groups this function is
    allowed to add **or remove**.  Groups outside this set are left
    untouched (avoids accidentally removing manually assigned groups).

    If ``managed_group_names`` is ``None``, the user's *current* group list
    is used as the managed boundary — effectively a full replacement.
    """
    target_group_names = set(target_group_names or [])

    if managed_group_names is None:
        managed_group_names = set(
            user.groups.values_list("name", flat=True)
        )
    else:
        managed_group_names = set(managed_group_names)

    current_managed = set(
        user.groups.filter(name__in=managed_group_names).values_list(
            "name", flat=True
        )
    )

    to_add = target_group_names - current_managed
    to_remove = current_managed - target_group_names

    if to_add:
        groups_map = ensure_groups(to_add)
        user.groups.add(*groups_map.values())

    if to_remove:
        user.groups.remove(*Group.objects.filter(name__in=to_remove))


# ---------------------------------------------------------------------------
# Claim extraction helpers
# ---------------------------------------------------------------------------

def extract_claim_groups(claims: dict, claim_keys=None) -> list:
    """
    Extract group/role names from OIDC claims.

    ``claim_keys`` defaults to ``SSO_CLAIM_GROUP_KEYS`` (``("groups", "roles")``).
    Each key may hold a list of strings or a whitespace-separated string.
    """
    if claim_keys is None:
        claim_keys = sso_settings.SSO_CLAIM_GROUP_KEYS

    claims = claims or {}
    values: list[str] = []
    for key in claim_keys:
        raw = claims.get(key)
        if isinstance(raw, list):
            values.extend(str(item) for item in raw if item)
        elif isinstance(raw, str) and raw.strip():
            values.extend(part for part in raw.split() if part)
    return sorted(set(values))


def extract_claim_scopes(claims: dict) -> list:
    """
    Extract OAuth2 scope strings from token claims.

    Checks ``granted_scopes`` (list) then ``scope`` (space-separated string).
    """
    claims = claims or {}
    granted = claims.get("granted_scopes")
    if isinstance(granted, list):
        return [str(s) for s in granted if s]
    scope = claims.get("scope")
    if isinstance(scope, str):
        return [part for part in scope.split() if part]
    return []


def build_scope_group_names(scopes: list, prefix: str | None = None) -> set:
    """
    Convert a list of OAuth2 scope strings to Django group names.

    e.g. ``"cms.write"`` → ``"SSO_SCOPE_CMS_WRITE"``
    """
    if prefix is None:
        prefix = sso_settings.SSO_SCOPE_GROUP_PREFIX
    return {
        f"{prefix}{scope.replace('.', '_').upper()}"
        for scope in (scopes or [])
    }


# ---------------------------------------------------------------------------
# Default sync handler
# ---------------------------------------------------------------------------

def _get_profile_model():
    """
    Return the SSOUserProfile model class selected by ``SSO_USER_PROFILE_MODEL``.

    Deferred to runtime to avoid import-time circular references.
    """
    model_path = sso_settings.SSO_USER_PROFILE_MODEL
    try:
        return apps.get_model(model_path)
    except (LookupError, ValueError) as exc:
        raise LookupError(
            f"SSO_USER_PROFILE_MODEL '{model_path}' could not be resolved. "
            f"Make sure the app is in INSTALLED_APPS and the model exists. "
            f"Original error: {exc}"
        ) from exc


def map_sso_user(sso_id: str, username: str, email: str | None, claims: dict | None = None):
    """
    Default ``SSO_USER_SYNC_HANDLER``.

    1. Upserts the Django User.
    2. Creates / updates the SSOUserProfile (if ``SSO_USER_PROFILE_MODEL`` is set).
    3. Syncs OIDC claim groups.
    4. Syncs scope-derived groups.

    Returns the User instance.
    """
    claims = claims or {}

    user, _ = upsert_user_by_username(username=username, email=email)

    # ── Profile ────────────────────────────────────────────────────────── #
    try:
        ProfileModel = _get_profile_model()
        profile, profile_created = ProfileModel.objects.get_or_create(
            user=user,
            defaults={"sso_id": sso_id, "extra_data": claims},
        )
        claims_changed = profile_created
        update_fields = []

        if profile.sso_id != sso_id:
            profile.sso_id = sso_id
            update_fields.append("sso_id")

        if (profile.extra_data or {}) != claims:
            profile.extra_data = claims
            update_fields.append("extra_data")
            claims_changed = True

        if update_fields:
            profile.save(update_fields=update_fields)

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Could not update SSO profile for user %s: %s", username, exc
        )
        claims_changed = True  # still sync groups even if profile write fails

    role_to_group_map = sso_settings.ROLE_TO_GROUP_MAP or {}
    scope_to_group_map = sso_settings.SCOPE_TO_GROUP_MAP or {}

    # ── Claim groups ───────────────────────────────────────────────────── #
    # Re-apply mapping on each authenticated sync call so drifted memberships
    # are corrected even when claims are unchanged.
    if claims:
        claim_groups = extract_claim_groups(claims)
        claim_groups = [role_to_group_map.get(group_name, group_name) for group_name in claim_groups]
        current_claim_groups = set(
            user.groups.filter(name__in=claim_groups).values_list("name", flat=True)
        )
        managed = set(claim_groups) | current_claim_groups
        sync_groups(user, claim_groups, managed_group_names=managed)

    # ── Scope groups ───────────────────────────────────────────────────── #
    prefix = sso_settings.SSO_SCOPE_GROUP_PREFIX
    scopes = extract_claim_scopes(claims)
    target_scope_groups = build_scope_group_names(scopes, prefix=prefix)

    # Optional explicit mapping from scope value -> Django group name.
    # When configured, these groups are also ensured and synced.
    mapped_scope_groups = {
        scope_to_group_map[scope]
        for scope in scopes
        if scope in scope_to_group_map
    }
    target_scope_groups |= mapped_scope_groups

    current_scope_groups = set(
        user.groups.filter(name__startswith=prefix).values_list("name", flat=True)
    )
    managed_scope_groups = target_scope_groups | current_scope_groups
    sync_groups(user, target_scope_groups, managed_group_names=managed_scope_groups)

    return user


def map_sso_user_minimal(sso_id: str, username: str, email: str | None, claims: dict | None = None):
    """
    Minimal sync handler — creates / updates the User only, no profile or
    group sync.  Suitable as a starting point for custom handlers or for
    projects that manage groups separately.
    """
    user, _ = upsert_user_by_username(username=username, email=email)
    return user
