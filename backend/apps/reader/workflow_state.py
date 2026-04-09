from __future__ import annotations

from datetime import date as date_type
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.core.bench_config import get_bench_configuration, get_required_judge_groups
from apps.judge.models import CourtroomJudgeDecision
from apps.listing.models import CauseList

from .models import BenchWorkflowState


def _primary_assignable_reader_for_bench(bench_key: str) -> int | None:
    bench = get_bench_configuration(bench_key)
    if not bench:
        return None
    required = tuple(bench.judge_groups)
    if not required:
        return None
    primary_group = required[0]
    mapping = dict(bench.reader_user_ids_by_group or ())
    reader_id = mapping.get(primary_group)
    return int(reader_id) if reader_id else None


def _recompute_all_required_approved(state: BenchWorkflowState) -> bool:
    required = tuple(state.required_role_groups or [])
    decisions = dict(state.decision_by_role or {})
    if not required:
        return False
    return all(bool((decisions.get(role) or {}).get("approved")) for role in required)


@transaction.atomic
def upsert_state_on_forward(
    *,
    efiling_id: int,
    forwarded_for_date: date_type,
    bench_key: str,
    forwarded_by: User | None = None,
) -> BenchWorkflowState:
    required = list(get_required_judge_groups(bench_key))
    state, _ = BenchWorkflowState.objects.get_or_create(
        efiling_id=efiling_id,
        forwarded_for_date=forwarded_for_date,
        bench_key=bench_key,
        defaults={
            "required_role_groups": required,
            "decision_by_role": {},
            "reader_visible": False,
        },
    )
    state.required_role_groups = required
    state.assignable_reader_user_id = _primary_assignable_reader_for_bench(bench_key)
    if forwarded_by:
        state.updated_by = forwarded_by
    state.all_required_approved = _recompute_all_required_approved(state)
    state.reader_visible = state.all_required_approved
    state.save(
        update_fields=[
            "required_role_groups",
            "assignable_reader_user",
            "all_required_approved",
            "reader_visible",
            "updated_by",
            "updated_at",
        ]
    )
    return state


@transaction.atomic
def apply_judge_decision(
    *,
    efiling_id: int,
    forwarded_for_date: date_type,
    bench_key: str,
    bench_role_group: str,
    judge_user_id: int,
    status: str,
    approved: bool,
    decision_notes: str | None = None,
) -> BenchWorkflowState:
    state = upsert_state_on_forward(
        efiling_id=efiling_id,
        forwarded_for_date=forwarded_for_date,
        bench_key=bench_key,
    )
    by_role: dict[str, Any] = dict(state.decision_by_role or {})
    by_role[bench_role_group] = {
        "approved": bool(approved),
        "status": str(status or ""),
        "decision_notes": (decision_notes or "").strip() or None,
        "judge_user_id": int(judge_user_id),
        "decided_at": timezone.now().isoformat(),
    }
    state.decision_by_role = by_role
    state.all_required_approved = _recompute_all_required_approved(state)
    state.reader_visible = state.all_required_approved
    state.save(
        update_fields=[
            "decision_by_role",
            "all_required_approved",
            "reader_visible",
            "updated_at",
        ]
    )
    return state


@transaction.atomic
def apply_reader_assign_date(
    *,
    efiling_ids: list[int],
    forwarded_for_date: date_type,
    listing_date: date_type,
    listing_remark: str | None,
    assigned_by: User | None = None,
) -> int:
    qs = BenchWorkflowState.objects.filter(
        efiling_id__in=list(efiling_ids),
        forwarded_for_date=forwarded_for_date,
    )
    updates = {
        "listing_date": listing_date,
        "listing_date_assigned_at": timezone.now(),
        "listing_remark": listing_remark,
        "updated_at": timezone.now(),
    }
    if assigned_by:
        updates["listing_assigned_by"] = assigned_by
        updates["updated_by"] = assigned_by
    return qs.update(**updates)


@transaction.atomic
def apply_cause_list_published(cause_list: CauseList) -> int:
    return BenchWorkflowState.objects.filter(
        forwarded_for_date=cause_list.cause_list_date,
        bench_key=cause_list.bench_key,
        efiling_id__in=cause_list.entries.filter(included=True).values_list("efiling_id", flat=True),
    ).update(
        is_published=True,
        published_at=timezone.now(),
        updated_at=timezone.now(),
    )


def state_approved_for_registered_cases(
    *,
    efiling_id: int,
    forwarded_for_date: date_type,
    bench_key: str,
) -> BenchWorkflowState | None:
    return BenchWorkflowState.objects.filter(
        efiling_id=efiling_id,
        forwarded_for_date=forwarded_for_date,
        bench_key=bench_key,
    ).first()
