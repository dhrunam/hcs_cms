"""
Bulk approval checks using bench_role_group with legacy fallback to Django auth groups.
"""

from __future__ import annotations

from typing import Iterable, Set

from django.db.models import Q, QuerySet

from apps.core.bench_config import get_required_judge_groups
from apps.judge.models import CourtroomJudgeDecision


def decision_matches_required_role(group_name: str) -> Q:
    """Prefer bench_role_group; fall back to legacy judge_user__groups__name."""
    legacy_slot = (Q(bench_role_group__isnull=True) | Q(bench_role_group="")) & Q(
        judge_user__groups__name=group_name
    )
    return Q(bench_role_group=group_name) | legacy_slot


def legacy_role_from_user_for_bench(user, required_groups: tuple[str, ...]) -> str | None:
    """Infer role for old rows without bench_role_group."""
    if not required_groups:
        return None

    names = set(user.groups.values_list("name", flat=True))
    token_match = names & set(required_groups)
    if len(token_match) == 1:
        return next(iter(token_match))
    if len(token_match) > 1:
        # Ambiguous token membership must not collapse to a single slot.
        return None
    if "JUDGE" in names and len(required_groups) == 1:
        return required_groups[0]
    return None


def efiling_ids_with_all_required_approvals(
    *,
    bench_key: str,
    efiling_ids: Iterable[int],
    forwarded_for_date=None,
    listing_date=None,
) -> Set[int]:
    """
    efiling_ids that have approved=True for each required judge group (by role),
    optionally filtered by forwarded_for_date and/or listing_date.
    """
    required = get_required_judge_groups(bench_key)
    if not required:
        return set()

    ids: Set[int] = {int(x) for x in efiling_ids}
    if not ids:
        return set()

    for group_name in required:
        qs: QuerySet = CourtroomJudgeDecision.objects.filter(
            decision_matches_required_role(group_name),
            efiling_id__in=ids,
            approved=True,
        )
        if forwarded_for_date is not None:
            qs = qs.filter(forwarded_for_date=forwarded_for_date)
        if listing_date is not None:
            qs = qs.filter(listing_date=listing_date)
        ids = set(qs.values_list("efiling_id", flat=True))
        if not ids:
            return set()
    return ids
