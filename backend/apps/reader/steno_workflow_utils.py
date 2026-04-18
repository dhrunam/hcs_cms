"""Shared helpers for steno order workflow (reader + judge apps)."""

from __future__ import annotations

from apps.core.bench_config import get_bench_configuration_for_stored_value

from apps.reader.models import StenoOrderWorkflow


def required_judge_user_ids_for_workflow(workflow: StenoOrderWorkflow) -> list[int]:
    cfg = get_bench_configuration_for_stored_value(getattr(workflow.efiling, "bench", None))
    if not cfg:
        return []
    return [int(uid) for uid in (cfg.judge_user_ids or ()) if uid]


def is_division_bench_steno_workflow(workflow: StenoOrderWorkflow) -> bool:
    return len(required_judge_user_ids_for_workflow(workflow)) > 1


def senior_judge_user_id_for_workflow(workflow: StenoOrderWorkflow) -> int | None:
    ids = required_judge_user_ids_for_workflow(workflow)
    return ids[0] if ids else None
