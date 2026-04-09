"""
Resolve which canonical judge role (JUDGE_CJ, JUDGE_J1, …) a decision row represents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from apps.core.bench_config import JUDGE_GROUP_TO_BENCH_TOKEN, get_required_judge_groups
from apps.judge.models import JUDGE_GROUP_CJ

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

_TOKEN_GROUPS = frozenset(JUDGE_GROUP_TO_BENCH_TOKEN.keys())


def resolve_bench_role_group_for_forward(user: "AbstractUser", forward_bench_key: str) -> str:
    """
    Pick the single required group this user's decision should satisfy for forward_bench_key.

    Raises ValueError if the user cannot be mapped (e.g. division bench + only API_JUDGE).
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

    api_like = JUDGE_GROUP_CJ in names or "API_JUDGE" in names
    if api_like and len(required) == 1:
        return required[0]
    if api_like and len(required) > 1:
        raise ValueError(
            "This bench requires multiple judge roles; assign each judge user to a "
            "token group (JUDGE_CJ, JUDGE_J1, JUDGE_J2) or use separate judge accounts."
        )
    raise ValueError(
        "Cannot determine judge role for this bench; user needs a matching JUDGE_CJ/J1/J2 "
        "group or API_JUDGE for single-judge benches only."
    )
