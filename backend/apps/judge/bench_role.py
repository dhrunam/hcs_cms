"""
Resolve which bench slot (BENCH_S0, BENCH_S1, …) a judge decision row represents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from apps.core.bench_config import (
    GENERIC_JUDGE_GROUP,
    get_bench_configuration,
    get_required_judge_groups,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


def resolve_bench_role_group_for_forward(user: "AbstractUser", forward_bench_key: str) -> str:
    """
    Pick the single required bench_role_group string for this user's decision row.

    For **division (multi-seat) benches**, seating on the active bench configuration
    (`judge_user_ids` order = BENCH_S0, BENCH_S1, …) is authoritative. That prevents
    two co-judges from both resolving to the same slot when Django groups are missing
    or mis-set (e.g. both users only carry ``BENCH_S0``), which would block the
    second judge with "already recorded by another judge".

    Single-seat / legacy: explicit slot group on the user, else roster match, else
    generic JUDGE + bench roster.
    """
    required = tuple(get_required_judge_groups(forward_bench_key))
    if not required:
        raise ValueError(f"Unknown bench_key={forward_bench_key!r}")

    bench = get_bench_configuration(forward_bench_key)
    if not bench:
        raise ValueError(
            f"No bench configuration for bench_key={forward_bench_key!r}.",
        )

    uids = tuple(bench.judge_user_ids or ())
    uid = int(user.pk)

    # Multi-seat: roster first (independent per-judge slots; not driven by shared flags).
    if len(required) > 1 and uids:
        seated_ids = {int(x) for x in uids}
        if uid in seated_ids:
            for i, judge_uid in enumerate(uids):
                if int(judge_uid) == uid and i < len(required):
                    return str(required[i])
        # Logged-in user not on roster: fall through for legacy / partial configs.

    names = set(user.groups.values_list("name", flat=True))
    matched = names & set(required)
    if len(matched) == 1:
        return next(iter(matched))
    if len(matched) > 1:
        raise ValueError(
            "Ambiguous judge role membership for this bench; assign exactly one "
            "bench slot group matching required roles.",
        )

    if GENERIC_JUDGE_GROUP not in names:
        raise ValueError(
            "Cannot determine judge role for this bench; user needs the JUDGE group "
            "or a bench slot group matching this bench.",
        )

    if not uids and len(required) == 1:
        return required[0]
    if not uids:
        raise ValueError(
            f"No active bench configuration for bench_key={forward_bench_key!r}.",
        )
    for i, judge_uid in enumerate(uids):
        if int(judge_uid) == uid and i < len(required):
            return str(required[i])
    raise ValueError(
        "This judge user is not seated on the configured bench for this bench_key.",
    )
