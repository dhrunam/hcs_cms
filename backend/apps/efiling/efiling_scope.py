"""
Restrict e-filing list/detail querysets to the owning advocate (created_by) when the
request user is an advocate-only role. Court / scrutiny / judge / reader roles keep
a global view of filings.
"""

from __future__ import annotations

from django.contrib.auth.models import AnonymousUser

# SSO-synced group names (see frontend auth.service dashboardRouteForRole).
_ADVOCATE_GROUP_NAMES = frozenset(
    {
        "ADVOCATE",
        "API_ADVOCATE",
    }
)

# Roles that must see all e-filings for operational workflows (not advocate-scoped).
_GLOBAL_EFILING_VIEW_GROUP_NAMES = frozenset(
    {
        "SCRUTINY_OFFICER",
        "API_SCRUTINY_OFFICER",
        "API_COURT_READER",
        "READER",
        "READER_CJ",
        "READER_J1",
        "READER_J2",
        "LISTING_OFFICER",
        "API_LISTING_OFFICER",
        "API_JUDGE",
        "JUDGE_CJ",
        "JUDGE_J1",
        "JUDGE_J2",
        "API_STENOGRAPHER",
    }
)


def should_scope_efilings_to_creator(user) -> bool:
    """
    Return True when list/detail querysets should filter to Efiling.created_by == user.

    Anonymous users: False (no extra filter; DRF auth should reject anyway).
    Superuser/staff: False (administrative access).
    Users with any global court role: False.
    Users with an advocate group and no global role: True.
    Otherwise: False (unknown roles — do not hide rows by default).
    """
    if user is None or isinstance(user, AnonymousUser):
        return False
    if not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return False

    names = set(user.groups.values_list("name", flat=True))
    if names & _GLOBAL_EFILING_VIEW_GROUP_NAMES:
        return False
    if names & _ADVOCATE_GROUP_NAMES:
        return True
    return False
