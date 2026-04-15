"""DRF permission classes for accounts / management APIs."""

from __future__ import annotations

from rest_framework import permissions


def user_is_staff_or_superadmin_group(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_staff", False):
        return True
    return user.groups.filter(name="SUPERADMIN").exists()


class IsStaffOrSuperAdminGroup(permissions.BasePermission):
    """
    Django staff (`is_staff`) or member of the SUPERADMIN auth group.
    Used for management list endpoints when JWT users may not have `is_staff`.
    """

    def has_permission(self, request, view) -> bool:
        return user_is_staff_or_superadmin_group(request.user)
