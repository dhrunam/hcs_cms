"""
Resolve which canonical judge role (JUDGE_CJ, JUDGE_J1, …) a decision row represents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from apps.core.bench_config import (
    GENERIC_JUDGE_GROUP,
    JUDGE_GROUP_TO_BENCH_TOKEN,
    get_bench_configuration,
    get_required_judge_groups,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

_TOKEN_GROUPS = frozenset(JUDGE_GROUP_TO_BENCH_TOKEN.keys())


def resolve_bench_role_group_for_forward(user: "AbstractUser", forward_bench_key: str) -> str:
    """
    Pick the single required bench_role_group string for this user's decision row.

    Uses legacy Django slot groups when present; otherwise maps generic JUDGE users by
    active bench configuration (judge_user_ids order matches required roles).
    """
    required = tuple(get_required_judge_groups(forward_bench_key))
    if not required:
        raise ValueError(f"Unknown bench_key={forward_bench_key!r}")

    names = set(user.groups.values_list("name", flat=True))
    matched = names & set(required) & _TOKEN_GROUPS
    if len(matched) == 1:
        return next(iter(matched))
    if len(matched) > 1:
        raise ValueError(
            "Ambiguous judge role membership for this bench; assign exactly one "
            "token group (JUDGE_CJ/JUDGE_J1/JUDGE_J2)."
        )

    if GENERIC_JUDGE_GROUP not in names:
        raise ValueError(
            "Cannot determine judge role for this bench; user needs the JUDGE group "
            "or a legacy JUDGE_CJ/JUDGE_J1/JUDGE_J2 group matching this bench."
        )

    bench = get_bench_configuration(forward_bench_key)
    if not bench:
        raise ValueError(
            f"No bench configuration for bench_key={forward_bench_key!r}."
        )
    # Legacy configs (no active bench_t) have empty judge_user_ids; single-slot benches
    # still map generic JUDGE to the one required role.
    if not bench.judge_user_ids and len(required) == 1:
        return required[0]
    if not bench.judge_user_ids:
        raise ValueError(
            f"No active bench configuration for bench_key={forward_bench_key!r}."
        )
    uid = int(user.pk)
    for i, judge_uid in enumerate(bench.judge_user_ids):
        if int(judge_uid) == uid and i < len(required):
            return required[i]
    raise ValueError(
        "This judge user is not seated on the configured bench for this bench_key."
    )
