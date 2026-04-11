"""
Application role keys (JWT claims / permission checks) and Django Group names.

Self-registration is allowed only for PARTY_IN_PERSON and ADVOCATE.
Other roles are staff-provisioned (Django admin or create_staff_user command).
"""

from __future__ import annotations

# Canonical role keys used in APIs, JWT claims, and view-level role checks
ROLE_ADVOCATE = "advocate"
ROLE_PARTY_IN_PERSON = "party_in_person"
ROLE_SCRUTINY_OFFICER = "scrutiny_officer"
ROLE_READER = "reader"
ROLE_LISTING_OFFICER = "listing_officer"
ROLE_STENO = "steno"
ROLE_JUDGE = "judge"
ROLE_SUPERADMIN = "superadmin"

# Django auth Group.name values (stable; referenced by frontend session / JWT)
GROUP_ADVOCATE = "ADVOCATE"
GROUP_PARTY_IN_PERSON = "PARTY_IN_PERSON"
GROUP_SCRUTINY_OFFICER = "SCRUTINY_OFFICER"
GROUP_READER = "READER"
GROUP_LISTING_OFFICER = "LISTING_OFFICER"
GROUP_STENO = "STENO"
GROUP_JUDGE = "JUDGE"
GROUP_SUPERADMIN = "SUPERADMIN"

ALL_ROLE_KEYS: tuple[str, ...] = (
    ROLE_ADVOCATE,
    ROLE_PARTY_IN_PERSON,
    ROLE_SCRUTINY_OFFICER,
    ROLE_READER,
    ROLE_LISTING_OFFICER,
    ROLE_STENO,
    ROLE_JUDGE,
    ROLE_SUPERADMIN,
)

ALL_GROUP_NAMES: tuple[str, ...] = (
    GROUP_ADVOCATE,
    GROUP_PARTY_IN_PERSON,
    GROUP_SCRUTINY_OFFICER,
    GROUP_READER,
    GROUP_LISTING_OFFICER,
    GROUP_STENO,
    GROUP_JUDGE,
    GROUP_SUPERADMIN,
)

# Maps token "role" keys / required_roles → Django Group.name
ROLE_TO_GROUP_MAP: dict[str, str] = {
    ROLE_ADVOCATE: GROUP_ADVOCATE,
    ROLE_PARTY_IN_PERSON: GROUP_PARTY_IN_PERSON,
    ROLE_SCRUTINY_OFFICER: GROUP_SCRUTINY_OFFICER,
    ROLE_READER: GROUP_READER,
    ROLE_LISTING_OFFICER: GROUP_LISTING_OFFICER,
    ROLE_STENO: GROUP_STENO,
    ROLE_JUDGE: GROUP_JUDGE,
    ROLE_SUPERADMIN: GROUP_SUPERADMIN,
}

SELF_REGISTRATION_ROLE_KEYS: frozenset[str] = frozenset({ROLE_ADVOCATE, ROLE_PARTY_IN_PERSON})

STAFF_PROVISIONED_ROLE_KEYS: frozenset[str] = frozenset(ALL_ROLE_KEYS) - SELF_REGISTRATION_ROLE_KEYS

# User.registration_type values
REG_PARTY = "party_in_person"
REG_ADVOCATE = "advocate"
REGISTRATION_TYPE_CHOICES = (
    (REG_PARTY, "Party in person"),
    (REG_ADVOCATE, "Advocate"),
)
