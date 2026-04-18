from __future__ import annotations

import mimetypes
from typing import List
from datetime import date as date_type
import logging
from pathlib import Path

from django.db import transaction
from django.db import connection
from django.db.models import Prefetch
from django.db.models import Q
from django.http import FileResponse
from django.urls import reverse
from django.utils import timezone
from django.core.files.storage import default_storage
from rest_framework import status as drf_status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Efiling, EfilingCaseDetails, EfilingDocumentsIndex, CivilT
from apps.core.models import ReaderJudgeAssignment, JudgeT, PurposeT
from apps.cis.models import OrderDetailsA
from apps.core.bench_config import (
    get_accessible_bench_codes_for_reader,
    get_accessible_bench_keys_for_reader,
    get_bench_configuration,
    get_bench_configuration_for_stored_value,
    get_bench_configurations,
    get_forward_bench_keys_for_reader,
    get_required_judge_groups,
    is_reader_date_authority_for_bench,
    is_reader_allowed_for_bench,
    mapped_judge_names_for_reader,
    resolved_efiling_bench_value,
)
from apps.efiling.party_display import build_petitioner_vs_respondent
from apps.efiling.pdf_validators import validate_pdf_file
from apps.judge.models import (
    CourtroomDecisionRequestedDocument,
    CourtroomJudgeDecision,
    JudgeDraftAnnotation,
    JudgeStenoMapping,
)
from apps.judge.courtroom_approval import (
    efiling_ids_with_all_required_approvals,
    legacy_role_from_user_for_bench,
)
from apps.listing.models import CauseList, CauseListEntry
from .models import (
    BenchWorkflowState,
    CourtroomForward,
    CourtroomForwardDocument,
    ReaderDailyProceeding,
    ReaderCaseReallocation,
    StenoOrderWorkflow,
    StenoWorkflowSignature,
)
from .workflow_state import (
    apply_reader_assign_date,
    upsert_state_on_forward,
)
from .serializers import (
    CourtroomForwardSerializer,
    AssignBenchesSerializer,
    ReaderCaseReallocationSerializer,
    ReaderDailyProceedingSubmitSerializer,
    StenoDraftUploadSerializer,
    StenoSubmitForJudgeSerializer,
    StenoResolveAnnotationSerializer,
    StenoShareForSignatureSerializer,
    StenoMarkSignatureSerializer,
)


def _steno_draft_preview_url(request, document_index_id: int | None) -> str | None:
    if not document_index_id:
        return None
    path = reverse(
        "efiling:efiling-document-index-stream",
        kwargs={"document_index_id": int(document_index_id)},
    )
    return request.build_absolute_uri(path)


def _steno_signed_preview_url(request, document_index_id: int | None) -> str | None:
    if not document_index_id:
        return None
    path = reverse(
        "efiling:efiling-document-index-stream",
        kwargs={"document_index_id": int(document_index_id)},
    )
    return request.build_absolute_uri(path)


def _resolve_efiling_cino(efiling: Efiling) -> str:
    case_number = (getattr(efiling, "case_number", None) or "").strip()
    if case_number:
        row = CivilT.objects.filter(case_no=case_number).values("cino").first()
        cino = (row or {}).get("cino")
        if cino:
            return str(cino)
    # Fallback for environments where civil_t bridge is incomplete.
    fallback = (case_number or (getattr(efiling, "e_filing_number", None) or "")).strip()
    if not fallback:
        raise ValidationError({"detail": "Unable to resolve CINO for this case."})
    return fallback[:16]


def _ensure_order_details_a_table_available() -> None:
    table_name = OrderDetailsA._meta.db_table
    with connection.cursor() as cursor:
        names = connection.introspection.table_names(cursor)
    if table_name not in names:
        raise ValidationError(
            {
                "detail": (
                    "CIS order table is unavailable (`order_details_a`). "
                    "Please provision the table before using steno order upload."
                )
            }
        )


def _next_order_no_for_cino(cino: str) -> int:
    latest = (
        OrderDetailsA.objects.filter(cino=cino)
        .order_by("-order_no")
        .values_list("order_no", flat=True)
        .first()
    )
    return int(latest or 0) + 1


def _store_steno_order_file(
    *,
    upload,
    efiling: Efiling,
    workflow_id: int,
    phase: str,
) -> str:
    efiling_folder = (
        (getattr(efiling, "e_filing_number", None) or getattr(efiling, "case_number", None) or "unknown")
        .strip()
        .replace("/", "_")
    )
    suffix = timezone.now().strftime("%Y%m%d%H%M%S")
    rel_path = f"efile/{efiling_folder}/orders/wf_{workflow_id}_{phase.lower()}_{suffix}.pdf"
    saved = default_storage.save(rel_path, upload)
    return default_storage.url(saved)


def _create_order_details_a_entry(
    *,
    efiling: Efiling,
    workflow_id: int,
    upload_url: str,
    phase: str,
    actor_login: str | None,
) -> OrderDetailsA:
    _ensure_order_details_a_table_available()
    cino = _resolve_efiling_cino(efiling)
    order_no = _next_order_no_for_cino(cino)
    now = timezone.now()
    case_no = (getattr(efiling, "case_number", None) or "")[:15] or None
    marker = f"STENO_WF_{workflow_id}_{phase.upper()}"
    return OrderDetailsA.objects.create(
        case_no=case_no,
        order_no=order_no,
        order_dt=now.date(),
        download=phase.upper(),
        upload=upload_url,
        doc_type=0,
        ordloc_lang="EN",
        timestamp=now,
        userlogin=actor_login,
        disp_nature=0,
        hashkey=marker,
        court_no=0,
        cino=cino,
        filing_no=(getattr(efiling, "e_filing_number", None) or "")[:15] or None,
        create_modify=now,
    )


def _latest_workflow_order_entry(efiling: Efiling, workflow_id: int, phase: str) -> OrderDetailsA | None:
    table_name = OrderDetailsA._meta.db_table
    with connection.cursor() as cursor:
        names = connection.introspection.table_names(cursor)
    if table_name not in names:
        return None
    cino = _resolve_efiling_cino(efiling)
    marker = f"STENO_WF_{workflow_id}_{phase.upper()}"
    return (
        OrderDetailsA.objects.filter(cino=cino, hashkey=marker)
        .order_by("-timestamp", "-order_no")
        .first()
    )


def _order_upload_preview_url(request, upload_value: str | None) -> str | None:
    raw = (upload_value or "").strip()
    if not raw:
        return None
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    if raw.startswith("/"):
        return request.build_absolute_uri(raw)
    return request.build_absolute_uri(f"/{raw}")


def _primary_steno_user_id_for_workflow(workflow: StenoOrderWorkflow) -> int | None:
    return workflow.assigned_steno_id


def _required_judge_user_ids_for_workflow(workflow: StenoOrderWorkflow) -> list[int]:
    cfg = get_bench_configuration_for_stored_value(getattr(workflow.efiling, "bench", None))
    if not cfg:
        return []
    return [int(uid) for uid in (cfg.judge_user_ids or ()) if uid]


def _all_required_signatures_done(workflow: StenoOrderWorkflow) -> bool:
    required = set(_required_judge_user_ids_for_workflow(workflow))
    if len(required) <= 1:
        return True
    rows = list(
        StenoWorkflowSignature.objects.filter(workflow=workflow, judge_user_id__in=required)
        .values("judge_user_id", "signature_status")
    )
    if len(rows) < len(required):
        return False
    signed = {
        int(r["judge_user_id"])
        for r in rows
        if r["signature_status"] == StenoWorkflowSignature.SignatureStatus.SIGNED
    }
    return required.issubset(signed)


_STENO_UPLOAD_ALLOWED = frozenset(
    {
        StenoOrderWorkflow.WorkflowStatus.PENDING_UPLOAD,
        StenoOrderWorkflow.WorkflowStatus.UPLOADED_BY_STENO,
        # Allow steno to replace draft while judge review is pending.
        StenoOrderWorkflow.WorkflowStatus.SENT_FOR_JUDGE_APPROVAL,
        StenoOrderWorkflow.WorkflowStatus.CHANGES_REQUESTED,
    }
)
logger = logging.getLogger(__name__)


def _approval_note_label_for_role(grp: str) -> str:
    if str(grp).startswith("BENCH_S"):
        return f"Seat {str(grp)[6:]}:"
    return str(grp).replace("JUDGE_", "Judge ")


def _get_reader_allowed_bench_keys(
    request,
    reader_group: str | None = None,
) -> set[str] | None:
    user = (
        request.user
        if getattr(request.user, 'is_authenticated', False)
        else None
    )
    return get_accessible_bench_keys_for_reader(
        user,
        reader_group=reader_group,
    )


def _get_reader_allowed_bench_codes(
    request,
    reader_group: str | None = None,
) -> set[str] | None:
    user = (
        request.user
        if getattr(request.user, 'is_authenticated', False)
        else None
    )
    return get_accessible_bench_codes_for_reader(
        user,
        reader_group=reader_group,
    )


def _get_reader_allowed_efiling_bench_filter(
    request,
    reader_group: str | None = None,
) -> Q | None:
    allowed_bench_codes = _get_reader_allowed_bench_codes(
        request,
        reader_group=reader_group,
    )
    allowed_bench_keys = _get_reader_allowed_bench_keys(
        request,
        reader_group=reader_group,
    )

    filter_q = Q()
    has_filter = False
    if allowed_bench_codes:
        filter_q |= Q(bench__in=allowed_bench_codes)
        has_filter = True
    if allowed_bench_keys is not None:
        if allowed_bench_keys:
            filter_q |= Q(bench__in=allowed_bench_keys)
        else:
            filter_q |= Q(pk__in=[])
        has_filter = True

    return filter_q if has_filter else None


def _assert_known_bench_key(bench_key: str) -> None:
    if get_bench_configuration(bench_key) is None:
        raise ValidationError({"bench_key": f"Unknown bench_key={bench_key}."})


def _assert_reader_can_access_case_for_current_bench(
    *,
    request,
    efiling_id: int,
    reader_group: str | None,
) -> None:
    if not getattr(request.user, "is_authenticated", False):
        raise ValidationError({"detail": "Authentication required."})
    allowed_bench_filter = _get_reader_allowed_efiling_bench_filter(
        request,
        reader_group=reader_group,
    )
    if allowed_bench_filter is None:
        return
    if not Efiling.objects.filter(allowed_bench_filter, id=efiling_id).exists():
        raise ValidationError({"detail": "You do not have permission to modify this case."})


def _delete_active_reader_bench_cycle(*, efiling: Efiling, bench_key: str) -> dict[str, int]:
    forward_qs = CourtroomForward.objects.filter(
        efiling=efiling,
        bench_key=bench_key,
    )
    forwarded_dates = set(forward_qs.values_list("forwarded_for_date", flat=True))
    forwarded_dates.update(
        BenchWorkflowState.objects.filter(
            efiling=efiling,
            bench_key=bench_key,
        ).values_list("forwarded_for_date", flat=True)
    )

    decision_count = 0
    if forwarded_dates:
        decision_count, _ = CourtroomJudgeDecision.objects.filter(
            efiling=efiling,
            forwarded_for_date__in=sorted(forwarded_dates),
        ).delete()

    workflow_count, _ = BenchWorkflowState.objects.filter(
        efiling=efiling,
        bench_key=bench_key,
    ).delete()
    forward_count, _ = forward_qs.delete()

    return {
        "deleted_decisions": int(decision_count),
        "deleted_workflow_states": int(workflow_count),
        "deleted_forwards": int(forward_count),
    }


def _reader_reallocation_user_name(user) -> str | None:
    if not user:
        return None
    full_name = " ".join(
        part.strip()
        for part in [
            getattr(user, "first_name", "") or "",
            getattr(user, "last_name", "") or "",
        ]
        if part and part.strip()
    ).strip()
    return full_name or getattr(user, "username", None)


def _reader_reallocation_bench_label(bench_key: str | None) -> str | None:
    normalized_key = str(bench_key or "").strip()
    if not normalized_key:
        return None
    bench = get_bench_configuration(normalized_key)
    return bench.label if bench else normalized_key


def _reader_reallocation_urls(request, reallocation: ReaderCaseReallocation) -> tuple[str | None, str | None]:
    if not reallocation.uploaded_order:
        return (None, None)
    path = reverse(
        "reader:reallocation-order-file",
        kwargs={"reallocation_id": int(reallocation.id)},
    )
    reader_group = str(request.query_params.get("reader_group", "")).strip()
    suffix = ""
    if reader_group:
        suffix = f"?reader_group={reader_group}"
    inline_url = request.build_absolute_uri(f"{path}{suffix}")
    download_url = request.build_absolute_uri(
        f"{path}?download=1"
        f"{'&reader_group=' + reader_group if reader_group else ''}"
    )
    return (inline_url, download_url)


def _serialize_reader_case_reallocation(request, reallocation: ReaderCaseReallocation) -> dict:
    order_file_url, order_file_download_url = _reader_reallocation_urls(
        request,
        reallocation,
    )
    return {
        "reallocation_id": int(reallocation.id),
        "previous_bench_key": reallocation.previous_bench_key,
        "previous_bench_label": _reader_reallocation_bench_label(
            reallocation.previous_bench_key,
        ),
        "new_bench_key": reallocation.new_bench_key,
        "new_bench_label": _reader_reallocation_bench_label(
            reallocation.new_bench_key,
        ),
        "remarks": reallocation.remarks,
        "reallocated_at": (
            reallocation.reallocated_at.isoformat()
            if reallocation.reallocated_at
            else None
        ),
        "reallocated_by_name": _reader_reallocation_user_name(
            reallocation.reallocated_by,
        ),
        "has_uploaded_order": bool(reallocation.uploaded_order),
        "order_file_url": order_file_url,
        "order_file_download_url": order_file_download_url,
    }


def _bench_filter_for_configuration(bench_config) -> Q:
    filter_q = Q(bench=bench_config.bench_key)
    if bench_config.bench_code:
        filter_q |= Q(bench=bench_config.bench_code)
    return filter_q


def _is_forward_relevant_to_bench(
    forward: CourtroomForward,
    bench_config,
    reader_slot_group: str | None = None,
    *,
    reader_user=None,
) -> bool:
    if reader_slot_group:
        if bench_config and forward.bench_key == bench_config.bench_key:
            if reader_user and getattr(forward.forwarded_by, "id", None) == reader_user.id:
                return True
            # Slot row is unique per (efiling, date, bench_key, bench_role_group). Match the
            # reader's slot even when forwarded_by is null or points at a different user id
            # (e.g. after DB restore / user id remap).
            if (forward.bench_role_group or "").strip() == (reader_slot_group or "").strip():
                return True
        forward_groups = tuple(get_required_judge_groups(forward.bench_key))
        return len(forward_groups) == 1 and forward_groups[0] == reader_slot_group
    forward_groups = set(get_required_judge_groups(forward.bench_key))
    bench_groups = set(bench_config.judge_groups)
    return bool(forward_groups) and forward_groups.issubset(bench_groups)


def _get_relevant_forwards_for_bench(
    forwards: list[CourtroomForward],
    bench_config,
    reader_slot_group: str | None = None,
    *,
    reader_user=None,
) -> list[CourtroomForward]:
    return [
        forward
        for forward in forwards
        if _is_forward_relevant_to_bench(
            forward,
            bench_config,
            reader_slot_group=reader_slot_group,
            reader_user=reader_user,
        )
    ]


def _overall_status_from_aggregate(approval_status: str) -> str:
    """Semantic status for reader UIs (division bench combined state)."""
    return {
        "NOT_FORWARDED": "not_forwarded",
        "PENDING": "in_review",
        "APPROVED": "ready_for_listing",
        "REJECTED": "rejected",
        "REQUESTED_DOCS": "requested_docs",
    }.get(approval_status, "not_forwarded")


def _build_judge_status_by_role(
    *,
    required_groups: tuple[str, ...],
    group_decisions: dict[str, bool],
    group_statuses: dict[str, str],
) -> dict[str, str]:
    """Per-slot judge lane for the active forward date (keys = bench_role_group)."""
    out: dict[str, str] = {}
    for gn in required_groups:
        appr = group_decisions.get(gn)
        st = (group_statuses.get(gn) or "").strip()
        if appr is True:
            out[gn] = "approved"
        elif appr is False:
            out[gn] = "rejected"
        elif st == "REQUESTED_DOCS":
            out[gn] = "requested_docs"
        elif st:
            out[gn] = "pending_review"
        else:
            out[gn] = "pending"
    return out


def _reader_bench_slot_key_for_forward(
    *,
    request,
    bench_key: str,
    reader_group: str | None,
) -> str:
    """Required judge slot (BENCH_Sn) for this reader on this bench; used as CourtroomForward key."""
    bench_config = get_bench_configuration(bench_key)
    if not bench_config:
        raise ValidationError({"bench_key": f"Unknown bench_key={bench_key}."})
    required = tuple(bench_config.judge_groups or ())
    reader_slot = _resolve_reader_slot_group_for_bench(
        request=request,
        bench_config=bench_config,
        reader_group=reader_group,
    )
    if len(required) == 1:
        return str(required[0])
    if reader_slot:
        return str(reader_slot)
    raise ValidationError(
        {
            "detail": (
                "Your reader account is not mapped to a division bench slot; "
                "cannot forward until ReaderJudgeAssignment / bench configuration is set."
            )
        }
    )


def _resolve_reader_slot_group_for_bench(
    *,
    request,
    bench_config,
    reader_group: str | None = None,
) -> str | None:
    if not bench_config:
        return None
    user = request.user if getattr(request.user, "is_authenticated", False) else None
    if user:
        mapping = dict(bench_config.reader_user_ids_by_group or ())
        for group_name, reader_user_id in mapping.items():
            if int(reader_user_id) == int(user.id):
                return str(group_name)
    if len(tuple(bench_config.judge_groups or ())) == 1:
        return str(tuple(bench_config.judge_groups)[0])
    return None


def _resolve_reader_approval_state(
    *,
    efiling_id: int,
    bench_config,
    relevant_forwards: list[CourtroomForward],
    decision_map: dict[tuple[int, date_type], dict[str, bool]],
    decision_status_map: dict[tuple[int, date_type], dict[str, str]],
    decision_notes_map: dict[tuple[int, date_type], List[str]],
    decision_listing_date_map: dict[tuple[int, date_type], List[str]],
    requested_docs_map: dict[tuple[int, date_type], List[dict]],
) -> dict:
    approval_status = "NOT_FORWARDED"
    approval_notes: list[str] = []
    approval_listing_date = None
    requested_documents: list[dict] = []
    approval_bench_key = None
    approval_forwarded_for_date = None
    listing_summary = (
        relevant_forwards[0].listing_summary
        if relevant_forwards
        else None
    )

    if not bench_config or not relevant_forwards:
        return {
            "approval_status": approval_status,
            "approval_notes": approval_notes,
            "approval_listing_date": approval_listing_date,
            "requested_documents": requested_documents,
            "approval_bench_key": approval_bench_key,
            "approval_forwarded_for_date": approval_forwarded_for_date,
            "listing_summary": listing_summary,
            "approved_all": False,
            "judge_status_by_role": {},
        }

    required_groups = tuple(bench_config.judge_groups)
    approval_bench_key = bench_config.bench_key

    chosen_dates_by_group: dict[str, date_type] = {}
    group_decisions: dict[str, bool] = {}
    group_statuses: dict[str, str] = {}
    selected_date_keys: list[tuple[int, date_type]] = []

    for forward in relevant_forwards:
        key = (efiling_id, forward.forwarded_for_date)
        approvals_for_date = decision_map.get(key, {})
        statuses_for_date = decision_status_map.get(key, {})
        matched_group = False

        for group_name in required_groups:
            if group_name in chosen_dates_by_group:
                continue
            if (
                group_name not in approvals_for_date
                and group_name not in statuses_for_date
            ):
                continue
            chosen_dates_by_group[group_name] = forward.forwarded_for_date
            if group_name in approvals_for_date:
                group_decisions[group_name] = approvals_for_date[group_name]
            if group_name in statuses_for_date:
                group_statuses[group_name] = statuses_for_date[group_name]
            matched_group = True

        if matched_group and key not in selected_date_keys:
            selected_date_keys.append(key)

        if len(chosen_dates_by_group) == len(required_groups):
            break

    if chosen_dates_by_group:
        approval_forwarded_for_date = max(
            chosen_dates_by_group.values(),
        ).isoformat()
    elif relevant_forwards:
        approval_forwarded_for_date = (
            relevant_forwards[0].forwarded_for_date.isoformat()
        )

    seen_notes: set[str] = set()
    seen_document_ids: set[int] = set()
    listing_dates: list[str] = []
    for key in selected_date_keys:
        for note in decision_notes_map.get(key, []):
            if note not in seen_notes:
                approval_notes.append(note)
                seen_notes.add(note)
        for listing_date in decision_listing_date_map.get(key, []):
            if listing_date not in listing_dates:
                listing_dates.append(listing_date)
        for requested_document in requested_docs_map.get(key, []):
            document_id = int(requested_document["document_index_id"])
            if document_id in seen_document_ids:
                continue
            requested_documents.append(requested_document)
            seen_document_ids.add(document_id)

    if listing_dates:
        approval_listing_date = sorted(listing_dates)[0]

    requested_docs = any(
        group_statuses.get(group_name) == "REQUESTED_DOCS"
        for group_name in required_groups
        if group_name in group_statuses
    )
    rejected = any(
        group_decisions.get(group_name) is False
        for group_name in required_groups
        if group_name in group_decisions
    )
    approved_all = bool(required_groups) and all(
        group_decisions.get(group_name) is True
        for group_name in required_groups
    )

    if requested_docs:
        approval_status = "REQUESTED_DOCS"
    elif rejected:
        approval_status = "REJECTED"
    elif approved_all:
        approval_status = "APPROVED"
    elif relevant_forwards:
        approval_status = "PENDING"

    judge_status_by_role = _build_judge_status_by_role(
        required_groups=required_groups,
        group_decisions=group_decisions,
        group_statuses=group_statuses,
    )

    return {
        "approval_status": approval_status,
        "approval_notes": approval_notes,
        "approval_listing_date": approval_listing_date,
        "requested_documents": requested_documents,
        "approval_bench_key": approval_bench_key,
        "approval_forwarded_for_date": approval_forwarded_for_date,
        "listing_summary": listing_summary,
        "approved_all": approved_all,
        "judge_status_by_role": judge_status_by_role,
    }


def _get_effective_forwarded_for_date(
    *,
    efiling: Efiling,
    requested_forwarded_for_date,
) -> date_type:
    """
    Use the reader's chosen calendar day for the CourtroomForward row.

    Reusing an older forward date caused the case to disappear from the judge dashboard
    for the selected day and broke courtroom APIs that matched URL date to forwarded_for_date.
    """
    return requested_forwarded_for_date


def _can_reader_assign_listing_date(
    request,
    bench_config,
    reader_group: str | None = None,
) -> bool:
    if not bench_config:
        return False

    user = (
        request.user
        if getattr(request.user, 'is_authenticated', False)
        else None
    )
    return is_reader_date_authority_for_bench(
        bench_config.bench_key,
        user,
        reader_group=reader_group,
    )


class BenchConfigurationsView(APIView):
    """
    Reader: expose active bench metadata for dynamic frontend rendering.
    """

    def get(self, request, *args, **kwargs):
        reader_group = request.query_params.get('reader_group')
        accessible_only = str(
            request.query_params.get('accessible_only', ''),
        ).lower() in {'1', 'true', 'yes'}
        allowed_bench_keys = _get_reader_allowed_bench_keys(
            request,
            reader_group=reader_group,
        )
        user = (
            request.user
            if getattr(request.user, 'is_authenticated', False)
            else None
        )
        forward_bench_keys = get_forward_bench_keys_for_reader(
            user,
            reader_group=reader_group,
        )

        items = []
        for bench in get_bench_configurations():
            is_accessible = (
                allowed_bench_keys is None
                or bench.bench_key in allowed_bench_keys
            )
            if accessible_only and not is_accessible:
                continue
            mapped_names = mapped_judge_names_for_reader(bench, user)
            items.append({
                'bench_key': bench.bench_key,
                'label': bench.label,
                'bench_code': bench.bench_code,
                'bench_name': bench.bench_name,
                'judge_names': list(bench.judge_names),
                'mapped_judge_names': list(mapped_names),
                'judge_user_ids': list(bench.judge_user_ids),
                'reader_user_ids': list(bench.reader_user_ids),
                'is_accessible_to_reader': is_accessible,
                'is_forward_target': bench.bench_key in forward_bench_keys,
            })

        return Response({'items': items}, status=drf_status.HTTP_200_OK)


class RegisteredCasesListView(APIView):
    """
    Reader: show scrutiny-completed (registered) cases.
    Identical to the previous Listing Officer view but now under Reader.
    """

    def get(self, request, *args, **kwargs):
        page_size_raw = request.query_params.get("page_size")
        page_size = int(page_size_raw) if page_size_raw not in (None, "", "null") else 200
        reader_group = request.query_params.get("reader_group")

        qs = Efiling.objects.filter(is_draft=False, status="ACCEPTED").order_by("-id")

        allowed_bench_filter = _get_reader_allowed_efiling_bench_filter(
            request,
            reader_group=reader_group,
        )
        if allowed_bench_filter is not None:
            qs = qs.filter(allowed_bench_filter)

        total = qs.count()

        case_details_qs = EfilingCaseDetails.objects.select_related("dispute_state", "dispute_district").order_by("id")
        qs = qs.prefetch_related(
            Prefetch("litigants"),
            Prefetch("case_details", queryset=case_details_qs),
        )

        efilings = list(qs[:page_size])
        efiling_ids = [e.id for e in efilings]
        latest_reallocation_by_efiling: dict[int, ReaderCaseReallocation] = {}
        if efiling_ids:
            for reallocation in (
                ReaderCaseReallocation.objects.filter(
                    efiling_id__in=efiling_ids,
                    is_active=True,
                )
                .select_related("reallocated_by")
                .order_by("efiling_id", "-reallocated_at", "-id")
            ):
                latest_reallocation_by_efiling.setdefault(
                    int(reallocation.efiling_id),
                    reallocation,
                )
        bench_groups_by_efiling: dict[int, tuple[str, ...]] = {}
        for e in efilings:
            cfg = get_bench_configuration_for_stored_value(e.bench)
            bench_groups_by_efiling[e.id] = tuple(cfg.judge_groups) if cfg else tuple()

        forwards_by_efiling: dict[int, list[CourtroomForward]] = {}
        forwards = (
            CourtroomForward.objects.filter(efiling_id__in=efiling_ids)
            .order_by("efiling_id", "-forwarded_for_date", "-id")
            .all()
        )
        for f in forwards:
            forwards_by_efiling.setdefault(f.efiling_id, []).append(f)

        forward_keys = {(f.efiling_id, f.forwarded_for_date) for f in forwards}
        decision_map: dict[tuple[int, date_type], dict[str, bool]] = {}
        decision_status_map: dict[tuple[int, date_type], dict[str, str]] = {}
        decision_notes_map: dict[tuple[int, date_type], List[str]] = {}
        decision_listing_date_map: dict[tuple[int, date_type], List[str]] = {}
        requested_docs_map: dict[tuple[int, date_type], List[dict]] = {}

        if forward_keys:
            e_ids = sorted({eid for eid, _ in forward_keys})
            f_dates = sorted({fdate for _, fdate in forward_keys})
            forward_heads: dict[tuple[int, date_type], CourtroomForward] = {}
            for f in (
                CourtroomForward.objects.filter(
                    efiling_id__in=e_ids,
                    forwarded_for_date__in=f_dates,
                ).order_by("efiling_id", "forwarded_for_date", "-id")
            ):
                k = (int(f.efiling_id), f.forwarded_for_date)
                if k not in forward_heads:
                    forward_heads[k] = f

            # Phase-A cutover: hydrate maps from canonical state table first.
            state_rows = BenchWorkflowState.objects.filter(
                efiling_id__in=e_ids,
                forwarded_for_date__in=f_dates,
            ).all()
            for st in state_rows:
                key = (int(st.efiling_id), st.forwarded_for_date)
                role_map = dict(st.decision_by_role or {})
                if role_map:
                    decision_map.setdefault(key, {})
                    decision_status_map.setdefault(key, {})
                for grp, payload in role_map.items():
                    if not grp:
                        continue
                    decision_map[key][str(grp)] = bool((payload or {}).get("approved"))
                    decision_status_map[key][str(grp)] = str((payload or {}).get("status") or "")
                    note_text = (payload or {}).get("decision_notes")
                    if note_text:
                        label = _approval_note_label_for_role(str(grp))
                        decision_notes_map.setdefault(key, []).append(f"{label}: {note_text}")
                if st.listing_date:
                    decision_listing_date_map.setdefault(key, []).append(str(st.listing_date))

            decision_rows = list(
                CourtroomJudgeDecision.objects.filter(
                    efiling_id__in=e_ids,
                    forwarded_for_date__in=f_dates,
                )
                .select_related("judge_user")
                .order_by("id")
            )
            decision_ids = [d.id for d in decision_rows]
            requested_rows = (
                CourtroomDecisionRequestedDocument.objects.filter(judge_decision_id__in=decision_ids)
                .select_related("judge_decision", "efiling_document_index")
                .values(
                    "judge_decision_id",
                    "efiling_document_index_id",
                    "efiling_document_index__document_part_name",
                    "efiling_document_index__document__document_type",
                )
                .all()
            )
            docs_by_decision: dict[int, List[dict]] = {}
            for rr in requested_rows:
                did = int(rr["judge_decision_id"])
                docs_by_decision.setdefault(did, []).append({
                    "document_index_id": rr["efiling_document_index_id"],
                    "document_part_name": rr.get("efiling_document_index__document_part_name"),
                    "document_type": rr.get("efiling_document_index__document__document_type"),
                })

            for d in decision_rows:
                key = (int(d.efiling_id), d.forwarded_for_date)
                fwd = forward_heads.get(key)
                req = bench_groups_by_efiling.get(int(d.efiling_id), tuple())
                if not req and fwd:
                    req = tuple(get_required_judge_groups(fwd.bench_key))
                grp = d.bench_role_group
                if (not grp) and req:
                    # Legacy fallback for old rows only. Ambiguous roles return None.
                    grp = legacy_role_from_user_for_bench(d.judge_user, req)
                if not grp:
                    continue
                if req and grp not in req:
                    continue
                if key not in decision_map:
                    decision_map[key] = {}
                    decision_status_map[key] = {}
                existing_approved = decision_map[key].get(grp)
                decision_map[key][grp] = bool(d.approved) if existing_approved is None else bool(existing_approved or d.approved)
                if grp not in decision_status_map[key]:
                    decision_status_map[key][grp] = str(d.status or "")

                note = (d.decision_notes or "").strip()
                if note:
                    if key not in decision_notes_map:
                        decision_notes_map[key] = []
                    label = _approval_note_label_for_role(str(grp))
                    decision_notes_map[key].append(f"{label}: {note}")

                lst_date = d.listing_date
                if lst_date:
                    decision_listing_date_map.setdefault(key, []).append(str(lst_date))

                decision_docs = docs_by_decision.get(int(d.id), [])
                if decision_docs:
                    existing = requested_docs_map.setdefault(key, [])
                    seen_ids = {x["document_index_id"] for x in existing}
                    for doc in decision_docs:
                        if doc["document_index_id"] not in seen_ids:
                            existing.append(doc)
                            seen_ids.add(doc["document_index_id"])

        items = []
        for e in efilings:
            latest_reallocation = latest_reallocation_by_efiling.get(int(e.id))
            respondent = next((l for l in e.litigants.all() if not getattr(l, "is_petitioner", False)), None)
            case_detail = e.case_details.all().first()
            approval_status = "NOT_FORWARDED"
            approval_notes = []
            approval_listing_date = None
            requested_documents = []
            approval_bench_key = None
            approval_forwarded_for_date = None
            can_assign_listing_date = False
            
            assigned_bench = get_bench_configuration_for_stored_value(e.bench)
            relevant_forwards = []
            reader_slot_forwards = []
            if assigned_bench:
                reader_slot_group = _resolve_reader_slot_group_for_bench(
                    request=request,
                    bench_config=assigned_bench,
                    reader_group=reader_group,
                )
                # Full bench-relevant forwards drive aggregate judge state (one or two rows per
                # day: a single shared forward is allowed; both readers still see the same
                # approval_status / overall_status).
                relevant_forwards = _get_relevant_forwards_for_bench(
                    forwards_by_efiling.get(e.id, []),
                    assigned_bench,
                )
                # Reader-slot forwards: rows this user created (forwarded_by); used for
                # listing_summary and my_forward_status only.
                reader_slot_forwards = _get_relevant_forwards_for_bench(
                    forwards_by_efiling.get(e.id, []),
                    assigned_bench,
                    reader_slot_group=reader_slot_group,
                    reader_user=request.user
                    if reader_slot_group
                    and getattr(request.user, "is_authenticated", False)
                    else None,
                )
                can_assign_listing_date = _can_reader_assign_listing_date(
                    request,
                    assigned_bench,
                    reader_group=reader_group,
                )

            approval_state = _resolve_reader_approval_state(
                efiling_id=e.id,
                bench_config=assigned_bench,
                relevant_forwards=relevant_forwards,
                decision_map=decision_map,
                decision_status_map=decision_status_map,
                decision_notes_map=decision_notes_map,
                decision_listing_date_map=decision_listing_date_map,
                requested_docs_map=requested_docs_map,
            )
            approval_status = approval_state["approval_status"]
            approval_notes = approval_state["approval_notes"]
            approval_listing_date = approval_state["approval_listing_date"]
            requested_documents = approval_state["requested_documents"]
            approval_bench_key = approval_state["approval_bench_key"]
            approval_forwarded_for_date = approval_state[
                "approval_forwarded_for_date"
            ]
            # Aggregate judge/forward state is not scrubbed by slot: both readers see the same
            # approval_status / overall_status for the bench. Per-reader forward ownership is
            # reported separately via my_forward_status and bench_has_forward.

            # Only expose listing_summary text from forwards this reader/slot owns (not bench-wide).
            listing_summary_for_response = None
            if reader_slot_forwards:
                slot_sorted = sorted(
                    reader_slot_forwards,
                    key=lambda fw: (fw.forwarded_for_date, fw.id),
                    reverse=True,
                )
                listing_summary_for_response = slot_sorted[0].listing_summary

            overall_status = _overall_status_from_aggregate(approval_status)
            my_forward_status = (
                "forwarded" if reader_slot_forwards else "not_forwarded"
            )
            bench_has_forward = bool(relevant_forwards)

            items.append({
                "efiling_id": e.id,
                "case_number": e.case_number,
                "e_filing_number": e.e_filing_number,
                "bench": e.bench,
                "bench_key": (
                    get_bench_configuration_for_stored_value(e.bench).bench_key
                    if get_bench_configuration_for_stored_value(e.bench)
                    else None
                ),
                "petitioner_name": e.petitioner_name,
                "respondent_name": getattr(respondent, "name", None) if respondent else None,
                "petitioner_vs_respondent": (e.petitioner_name or "").strip() or build_petitioner_vs_respondent(
                    e, fallback_petitioner_name=e.petitioner_name or ""
                ),
                "cause_of_action": getattr(case_detail, "cause_of_action", None) if case_detail else None,
                "approval_status": approval_status,
                "overall_status": overall_status,
                "my_forward_status": my_forward_status,
                "bench_has_forward": bench_has_forward,
                "all_judges_reviewed": bool(
                    approval_state.get("approved_all", False)
                ),
                "judge_status_by_role": approval_state.get(
                    "judge_status_by_role"
                )
                or {},
                "approval_notes": approval_notes,
                "approval_bench_key": approval_bench_key,
                "approval_forwarded_for_date": approval_forwarded_for_date,
                "approval_listing_date": approval_listing_date,
                "listing_summary": listing_summary_for_response,
                "requested_documents": requested_documents,
                "can_assign_listing_date": can_assign_listing_date,
                "is_reallocated_case": bool(latest_reallocation),
                "latest_reallocation_at": (
                    latest_reallocation.reallocated_at.isoformat()
                    if latest_reallocation and latest_reallocation.reallocated_at
                    else None
                ),
                "latest_reallocation_previous_bench_key": (
                    latest_reallocation.previous_bench_key
                    if latest_reallocation
                    else None
                ),
                "latest_reallocation_previous_bench_label": (
                    _reader_reallocation_bench_label(
                        latest_reallocation.previous_bench_key,
                    )
                    if latest_reallocation
                    else None
                ),
                "latest_reallocation_new_bench_key": (
                    latest_reallocation.new_bench_key
                    if latest_reallocation
                    else None
                ),
                "latest_reallocation_new_bench_label": (
                    _reader_reallocation_bench_label(
                        latest_reallocation.new_bench_key,
                    )
                    if latest_reallocation
                    else None
                ),
            })

        return Response({"total": total, "items": items}, status=drf_status.HTTP_200_OK)


class AssignBenchesView(APIView):
    """
    Reader: bulk-assign benches for registered cases.
    """

    def post(self, request, *args, **kwargs):
        payload = AssignBenchesSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        assignments = payload.validated_data["assignments"]

        if not assignments:
            return Response({"updated": 0}, status=drf_status.HTTP_200_OK)

        assign_map = {int(a["efiling_id"]): a["bench_key"] for a in assignments}
        for bench_key in assign_map.values():
            _assert_known_bench_key(bench_key)
        ef_qs = Efiling.objects.filter(id__in=assign_map.keys(), is_draft=False, status="ACCEPTED")
        ef_by_id = {e.id: e for e in ef_qs}

        updated_instances = []
        updated_at = timezone.now()
        acting_user = request.user if request.user.is_authenticated else None
        for eid, bench_key in assign_map.items():
            if eid in ef_by_id:
                e = ef_by_id[eid]
                bench_config = get_bench_configuration(bench_key)
                e.bench = resolved_efiling_bench_value(bench_config)
                e.updated_by = acting_user
                e.updated_at = updated_at
                updated_instances.append(e)

        Efiling.objects.bulk_update(updated_instances, ["bench", "updated_by", "updated_at"])
        return Response({"updated": len(updated_instances)}, status=drf_status.HTTP_200_OK)


class CourtroomForwardView(APIView):
    """
    Reader: forward selected efilings to judges.
    """

    def post(self, request, *args, **kwargs):
        payload = CourtroomForwardSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        forwarded_for_date = payload.validated_data["forwarded_for_date"]
        bench_key = payload.validated_data["bench_key"]
        listing_summary = payload.validated_data.get("listing_summary")
        document_index_ids = payload.validated_data.get("document_index_ids") or []
        efiling_ids = payload.validated_data["efiling_ids"]
        user = request.user if request.user.is_authenticated else None
        reader_group = request.query_params.get("reader_group")
        _assert_known_bench_key(bench_key)
        if not is_reader_allowed_for_bench(bench_key, user, reader_group=reader_group):
            raise ValidationError({"bench_key": "You do not have permission to forward to this bench."})

        slot_key = _reader_bench_slot_key_for_forward(
            request=request,
            bench_key=bench_key,
            reader_group=reader_group,
        )

        # Security: check if user can forward these efilings
        allowed_bench_filter = _get_reader_allowed_efiling_bench_filter(
            request,
            reader_group=reader_group,
        )
        if allowed_bench_filter is not None and efiling_ids:
            allowed_ids = list(
                Efiling.objects.filter(allowed_bench_filter, id__in=efiling_ids)
                .values_list("id", flat=True)
            )
            if len(allowed_ids) != len(efiling_ids):
                raise ValidationError("You do not have permission to forward some of these cases.")

        updated = 0
        for eid in efiling_ids:
            efiling = Efiling.objects.filter(
                id=eid,
                is_draft=False,
                status="ACCEPTED",
            ).first()
            if not efiling:
                continue
            effective_forwarded_for_date = _get_effective_forwarded_for_date(
                efiling=efiling,
                requested_forwarded_for_date=forwarded_for_date,
            )
            obj, _ = CourtroomForward.objects.update_or_create(
                efiling_id=eid,
                forwarded_for_date=effective_forwarded_for_date,
                bench_key=bench_key,
                bench_role_group=slot_key,
                defaults={
                    "forwarded_by": user,
                    "listing_summary": listing_summary,
                },
            )
            updated += 1
            upsert_state_on_forward(
                efiling_id=int(eid),
                forwarded_for_date=effective_forwarded_for_date,
                bench_key=bench_key,
                forwarded_by=user,
            )
            if document_index_ids:
                valid_doc_ids = set(EfilingDocumentsIndex.objects.filter(
                    id__in=document_index_ids, document__e_filing_id=eid
                ).values_list("id", flat=True))
                
                CourtroomForwardDocument.objects.filter(forward=obj).exclude(
                    efiling_document_index_id__in=valid_doc_ids
                ).delete()
                for doc_id in valid_doc_ids:
                    CourtroomForwardDocument.objects.get_or_create(
                        forward=obj, efiling_document_index_id=doc_id
                    )

        return Response({"updated": updated}, status=drf_status.HTTP_200_OK)


class ReaderApprovedCasesView(APIView):
    """
    Reader: list cases that have been approved by ALL required judges, but have NOT yet been assigned a listing_date.
    """

    def get(self, request, *args, **kwargs):
        bench_key = request.query_params.get("bench_key")
        forwarded_for_date = request.query_params.get("forwarded_for_date")

        if not bench_key or not forwarded_for_date:
            raise ValidationError({"bench_key": "Required.", "forwarded_for_date": "Required."})

        fwd_date = timezone.datetime.fromisoformat(forwarded_for_date).date()
        if not get_required_judge_groups(bench_key):
            raise ValidationError({"bench_key": f"Unknown bench_key={bench_key}."})

        bench_config = get_bench_configuration(bench_key)
        forwarded_efiling_ids = Efiling.objects.filter(
            _bench_filter_for_configuration(bench_config),
            id__in=CourtroomForward.objects.filter(
                forwarded_for_date=fwd_date,
            ).values_list("efiling_id", flat=True),
        )

        # FILTER BY READER ROLE
        reader_group = request.query_params.get("reader_group")
        allowed_bench_keys = _get_reader_allowed_bench_keys(request, reader_group=reader_group)
        if allowed_bench_keys is not None:
            if bench_key not in allowed_bench_keys:
                return Response({"results": []}, status=drf_status.HTTP_200_OK)
        forwarded_efiling_ids_list = list(forwarded_efiling_ids.values_list("id", flat=True))

        fully_approved = efiling_ids_with_all_required_approvals(
            bench_key=bench_key,
            efiling_ids=forwarded_efiling_ids_list,
            forwarded_for_date=fwd_date,
            listing_date=None,
        )
        approved_efiling_ids = []
        for eid in fully_approved:
            has_date = CourtroomJudgeDecision.objects.filter(
                efiling_id=eid, forwarded_for_date=fwd_date, listing_date__isnull=False
            ).exists()
            if not has_date:
                approved_efiling_ids.append(eid)

        efilings = Efiling.objects.filter(id__in=approved_efiling_ids)
        data = [{
            "id": ef.id,
            "e_filing_number": ef.e_filing_number,
            "case_number": ef.case_number,
            "petitioner_name": ef.petitioner_name,
            "bench": ef.bench,
            "forwarded_for_date": fwd_date.isoformat(),
        } for ef in efilings]

        return Response({"results": data}, status=drf_status.HTTP_200_OK)


class ReaderAssignDateView(APIView):
    """
    Reader: Assign a listing_date to one or more approved efilings.
    """

    def post(self, request, *args, **kwargs):
        efiling_ids = request.data.get("efiling_ids", [])
        ldate = request.data.get("listing_date")
        fwd_date = request.data.get("forwarded_for_date")
        lremark = request.data.get("listing_remark")
        user = request.user if getattr(request.user, "is_authenticated", False) else None

        if not efiling_ids or not ldate or not fwd_date:
            raise ValidationError({"efiling_ids": "Required.", "listing_date": "Required.", "forwarded_for_date": "Required."})

        # Security: check if user can assign dates to these efilings
        reader_group = request.query_params.get("reader_group")
        allowed_bench_filter = _get_reader_allowed_efiling_bench_filter(
            request,
            reader_group=reader_group,
        )
        if allowed_bench_filter is not None:
            allowed_ids = Efiling.objects.filter(
                allowed_bench_filter,
                id__in=efiling_ids,
            ).values_list("id", flat=True)
            if len(allowed_ids) != len(efiling_ids):
                raise ValidationError("You do not have permission to assign dates to some of these cases.")

        efilings = list(Efiling.objects.filter(id__in=efiling_ids))
        unauthorized_efiling_ids: list[int] = []
        for efiling in efilings:
            assigned_bench = get_bench_configuration_for_stored_value(efiling.bench)
            if not assigned_bench or not is_reader_date_authority_for_bench(
                assigned_bench.bench_key,
                user,
                reader_group=reader_group,
            ):
                unauthorized_efiling_ids.append(efiling.id)

        if unauthorized_efiling_ids:
            raise ValidationError({
                "efiling_ids": (
                    "Only the higher-priority bench reader can assign the listing date for "
                    f"these case(s): {', '.join(str(item) for item in unauthorized_efiling_ids)}."
                )
            })

        # Update all matching decisions. Note: in some cases (Division Bench) multiple judges 
        # have decisions for the same filing/date. We update all of them with the final date.
        updated = CourtroomJudgeDecision.objects.filter(
            efiling_id__in=efiling_ids, forwarded_for_date=fwd_date
        ).update(
            listing_date=ldate,
            reader_listing_remark=lremark,
            updated_by=user,
            updated_at=timezone.now(),
        )
        try:
            apply_reader_assign_date(
                efiling_ids=[int(x) for x in efiling_ids],
                forwarded_for_date=timezone.datetime.fromisoformat(str(fwd_date)).date(),
                listing_date=timezone.datetime.fromisoformat(str(ldate)).date(),
                listing_remark=lremark,
                assigned_by=user,
            )
        except Exception:
            logger.exception("bench workflow state assign-date dual-write failed")

        return Response({"updated": updated}, status=drf_status.HTTP_200_OK)

class ReaderResetBenchView(APIView):
    """
    Reader: Reset bench to None (Send back to Scrutiny).
    """

    def post(self, request, *args, **kwargs):
        efiling_id = request.data.get("efiling_id")
        if not efiling_id:
            raise ValidationError({"efiling_id": "Required."})
        reader_group = request.query_params.get("reader_group")
        _assert_reader_can_access_case_for_current_bench(
            request=request,
            efiling_id=int(efiling_id),
            reader_group=reader_group,
        )
        
        try:
            efiling = Efiling.objects.get(id=efiling_id)
        except Efiling.DoesNotExist:
            return Response({"detail": "Not found."}, status=drf_status.HTTP_404_NOT_FOUND)

        current_bench = get_bench_configuration_for_stored_value(efiling.bench)
        current_bench_key = current_bench.bench_key if current_bench else str(efiling.bench or "").strip()
        with transaction.atomic():
            if current_bench_key:
                _delete_active_reader_bench_cycle(
                    efiling=efiling,
                    bench_key=current_bench_key,
                )

            efiling.bench = None
            efiling.updated_by = request.user if getattr(request.user, "is_authenticated", False) else None
            efiling.save(update_fields=["bench", "updated_by", "updated_at"])
        
        return Response({"detail": "Bench reset successful. Case returned to Scrutiny pool."}, status=drf_status.HTTP_200_OK)


class ReaderReallocateCaseView(APIView):
    def post(self, request, *args, **kwargs):
        payload = ReaderCaseReallocationSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        efiling_id = int(payload.validated_data["efiling_id"])
        new_bench_key = payload.validated_data["new_bench_key"]
        remarks = payload.validated_data["remarks"].strip()
        order_file = payload.validated_data.get("order_file")
        reader_group = request.query_params.get("reader_group")
        acting_user = request.user if getattr(request.user, "is_authenticated", False) else None

        if not remarks:
            raise ValidationError({"remarks": "Remarks are required."})

        _assert_reader_can_access_case_for_current_bench(
            request=request,
            efiling_id=efiling_id,
            reader_group=reader_group,
        )
        _assert_known_bench_key(new_bench_key)

        efiling = Efiling.objects.filter(
            id=efiling_id,
            is_draft=False,
            status="ACCEPTED",
        ).first()
        if not efiling:
            raise ValidationError({"efiling_id": "Invalid case."})

        current_bench = get_bench_configuration_for_stored_value(efiling.bench)
        if not current_bench:
            raise ValidationError({"detail": "Case does not currently have an assigned bench."})
        if current_bench.bench_key == new_bench_key:
            raise ValidationError({"new_bench_key": "Please select a different bench."})

        if BenchWorkflowState.objects.filter(
            efiling=efiling,
            bench_key=current_bench.bench_key,
            listing_date__isnull=False,
        ).exists() or CourtroomJudgeDecision.objects.filter(
            efiling=efiling,
            listing_date__isnull=False,
        ).exists():
            raise ValidationError({
                "detail": "Case cannot be reallocated after a listing date has been assigned."
            })

        if order_file is not None:
            validate_pdf_file(order_file, "order_file")

        new_bench = get_bench_configuration(new_bench_key)
        if not new_bench:
            raise ValidationError({"new_bench_key": "Invalid bench selection."})

        with transaction.atomic():
            cleanup_result = _delete_active_reader_bench_cycle(
                efiling=efiling,
                bench_key=current_bench.bench_key,
            )

            efiling.bench = resolved_efiling_bench_value(new_bench)
            efiling.updated_by = acting_user
            efiling.save(update_fields=["bench", "updated_by", "updated_at"])

            reallocation = ReaderCaseReallocation.objects.create(
                efiling=efiling,
                previous_bench_key=current_bench.bench_key,
                new_bench_key=new_bench.bench_key,
                remarks=remarks,
                uploaded_order=order_file,
                reallocated_by=acting_user,
                reallocated_at=timezone.now(),
                updated_by=acting_user,
            )

        return Response(
            {
                "detail": "Case reallocated successfully.",
                "reallocation_id": reallocation.id,
                "previous_bench_key": current_bench.bench_key,
                "new_bench_key": new_bench.bench_key,
                "new_bench_label": new_bench.label,
                **cleanup_result,
            },
            status=drf_status.HTTP_200_OK,
        )


class ReaderCaseReallocationHistoryView(APIView):
    def get(self, request, efiling_id: int, *args, **kwargs):
        reader_group = request.query_params.get("reader_group")
        _assert_reader_can_access_case_for_current_bench(
            request=request,
            efiling_id=int(efiling_id),
            reader_group=reader_group,
        )

        efiling = Efiling.objects.filter(
            id=efiling_id,
            is_draft=False,
            status="ACCEPTED",
        ).first()
        if not efiling:
            return Response(
                {"detail": "Not found."},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        reallocations = list(
            ReaderCaseReallocation.objects.filter(
                efiling_id=efiling_id,
                is_active=True,
            )
            .select_related("reallocated_by")
            .order_by("-reallocated_at", "-id")
        )

        items = [
            _serialize_reader_case_reallocation(request, reallocation)
            for reallocation in reallocations
        ]
        return Response(
            {
                "efiling_id": int(efiling_id),
                "total": len(items),
                "items": items,
            },
            status=drf_status.HTTP_200_OK,
        )


class ReaderReallocationOrderFileView(APIView):
    def get(self, request, reallocation_id: int, *args, **kwargs):
        if not getattr(request.user, "is_authenticated", False):
            raise ValidationError({"detail": "Authentication required."})

        reallocation = (
            ReaderCaseReallocation.objects.select_related("efiling")
            .filter(id=reallocation_id, is_active=True)
            .first()
        )
        if not reallocation or not reallocation.uploaded_order:
            return Response(
                {"detail": "Order file not found."},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        reader_group = request.query_params.get("reader_group")
        _assert_reader_can_access_case_for_current_bench(
            request=request,
            efiling_id=int(reallocation.efiling_id),
            reader_group=reader_group,
        )

        try:
            file_path = Path(reallocation.uploaded_order.path)
        except (NotImplementedError, ValueError):
            return Response(
                {"detail": "Order file is not available."},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        if not file_path.exists() or not file_path.is_file():
            return Response(
                {"detail": "Order file is not available."},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        content_type, _ = mimetypes.guess_type(str(file_path))
        download_requested = str(
            request.query_params.get("download", ""),
        ).lower() in {"1", "true", "yes"}
        filename = file_path.name or f"reallocation-order-{reallocation.id}.pdf"
        return FileResponse(
            file_path.open("rb"),
            as_attachment=download_requested,
            filename=filename,
            content_type=content_type or "application/pdf",
        )


def _resolve_judge_and_steno_for_reader_submission(
    *,
    request,
    efiling: Efiling,
    reader_group: str | None,
):
    acting_user = request.user if getattr(request.user, "is_authenticated", False) else None
    if not acting_user:
        return (None, None)
    assigned_bench = get_bench_configuration_for_stored_value(efiling.bench)
    bench_key = assigned_bench.bench_key if assigned_bench else None

    judge_t: JudgeT | None = None
    if assigned_bench and assigned_bench.judge_user_ids:
        for uid in assigned_bench.judge_user_ids:
            judge_t = JudgeT.objects.filter(user_id=uid).first()
            if judge_t:
                break
    if not judge_t:
        assignment = (
            ReaderJudgeAssignment.objects.filter(
                reader_user=acting_user,
                effective_to__isnull=True,
            )
            .select_related("judge")
            .first()
        )
        if assignment:
            judge_t = assignment.judge

    if not judge_t:
        return (None, None)

    mapping_qs = JudgeStenoMapping.objects.filter(
        judge_id=judge_t.id,
        is_active=True,
    )
    if bench_key:
        mapping_qs = mapping_qs.filter(Q(bench_key=bench_key) | Q(bench_key__isnull=True))
    steno_mapping = mapping_qs.order_by("-effective_from", "-id").first()
    judge_user_id = judge_t.user_id
    return (judge_user_id, steno_mapping.steno_user_id if steno_mapping else None)


class ReaderDailyProceedingsListView(APIView):
    def get(self, request, *args, **kwargs):
        reader_group = request.query_params.get("reader_group")
        cause_list_date_raw = request.query_params.get("cause_list_date")
        page_size_raw = request.query_params.get("page_size")
        page_size = int(page_size_raw) if page_size_raw not in (None, "", "null") else 200
        if not cause_list_date_raw:
            raise ValidationError({"cause_list_date": "Required. Use YYYY-MM-DD."})
        try:
            cause_list_date = timezone.datetime.fromisoformat(cause_list_date_raw).date()
        except (TypeError, ValueError):
            raise ValidationError({"cause_list_date": "Invalid date format. Use YYYY-MM-DD."})

        allowed_bench_filter = _get_reader_allowed_efiling_bench_filter(
            request,
            reader_group=reader_group,
        )
        state_published_ids = set(
            BenchWorkflowState.objects.filter(
                forwarded_for_date=cause_list_date,
                is_published=True,
            ).values_list("efiling_id", flat=True)
        )
        legacy_published_ids = set(
            CauseListEntry.objects.filter(
                cause_list__cause_list_date=cause_list_date,
                cause_list__status=CauseList.CauseListStatus.PUBLISHED,
                included=True,
            ).values_list("efiling_id", flat=True)
        )
        if legacy_published_ids != state_published_ids:
            logger.warning(
                "bench workflow state mismatch daily proceedings date=%s state=%s legacy=%s",
                cause_list_date.isoformat(),
                len(state_published_ids),
                len(legacy_published_ids),
            )
        published_ids = state_published_ids or legacy_published_ids
        qs = Efiling.objects.filter(
            id__in=published_ids,
            is_draft=False,
            status="ACCEPTED",
        ).order_by("-id")
        if allowed_bench_filter is not None:
            qs = qs.filter(allowed_bench_filter)
        total = qs.count()
        efilings = list(qs[:page_size])
        ids = [x.id for x in efilings]

        latest_proceedings = {}
        for row in ReaderDailyProceeding.objects.filter(efiling_id__in=ids).select_related("steno_purpose").order_by(
            "efiling_id", "-hearing_date", "-id"
        ):
            latest_proceedings.setdefault(row.efiling_id, row)

        items = []
        for e in efilings:
            bench = get_bench_configuration_for_stored_value(e.bench)
            can_assign = _can_reader_assign_listing_date(
                request,
                bench,
                reader_group=reader_group,
            )
            proceeding = latest_proceedings.get(e.id)
            workflow = (
                proceeding.steno_workflows.order_by("-id").first()
                if proceeding
                else None
            )
            items.append(
                {
                    "efiling_id": e.id,
                    "case_number": e.case_number,
                    "e_filing_number": e.e_filing_number,
                    "petitioner_name": e.petitioner_name,
                    "bench": e.bench,
                    "bench_key": bench.bench_key if bench else None,
                    "last_hearing_date": (
                        proceeding.hearing_date.isoformat() if proceeding else None
                    ),
                    "last_next_listing_date": (
                        proceeding.next_listing_date.isoformat() if proceeding else None
                    ),
                    "latest_proceedings_text": (
                        proceeding.proceedings_text if proceeding else None
                    ),
                    "latest_steno_purpose_code": (
                        proceeding.steno_purpose_id if proceeding else None
                    ),
                    "latest_steno_purpose_name": (
                        proceeding.steno_purpose.purpose_name
                        if proceeding and proceeding.steno_purpose
                        else None
                    ),
                    "listing_sync_status": (
                        proceeding.listing_sync_status if proceeding else None
                    ),
                    "steno_workflow_status": (
                        workflow.workflow_status if workflow else None
                    ),
                    "can_assign_listing_date": can_assign,
                }
            )
        return Response({"total": total, "items": items}, status=drf_status.HTTP_200_OK)


class ReaderDailyProceedingsSubmitView(APIView):
    def post(self, request, *args, **kwargs):
        payload = ReaderDailyProceedingSubmitSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        reader_group = request.query_params.get("reader_group")
        user = request.user if getattr(request.user, "is_authenticated", False) else None
        efiling_id = payload.validated_data["efiling_id"]
        hearing_date = payload.validated_data["hearing_date"]
        next_listing_date = payload.validated_data["next_listing_date"]
        proceedings_text = payload.validated_data["proceedings_text"]
        steno_purpose_code = payload.validated_data.get("steno_purpose_code")
        legacy_reader_remark = payload.validated_data.get("reader_remark")
        steno_remark = payload.validated_data.get("steno_remark")
        listing_remark = payload.validated_data.get("listing_remark")
        steno_purpose = None
        if steno_purpose_code is not None:
            steno_purpose = PurposeT.objects.filter(
                purpose_code=steno_purpose_code,
                is_active=True,
            ).first()
            if steno_purpose is None:
                raise ValidationError({"steno_purpose_code": "Invalid purpose."})

        if steno_purpose is not None:
            resolved_steno_remark = steno_purpose.purpose_name or str(steno_purpose.purpose_code)
        elif steno_remark not in (None, ""):
            resolved_steno_remark = steno_remark
        elif legacy_reader_remark not in (None, ""):
            resolved_steno_remark = legacy_reader_remark
        else:
            resolved_steno_remark = None

        if listing_remark in (None, "") and legacy_reader_remark not in (None, ""):
            listing_remark = legacy_reader_remark
        document_type = payload.validated_data.get("document_type") or "ORDER"

        efiling = Efiling.objects.filter(
            id=efiling_id,
            is_draft=False,
            status="ACCEPTED",
        ).first()
        if not efiling:
            raise ValidationError({"efiling_id": "Invalid case."})
        assigned_bench = get_bench_configuration_for_stored_value(efiling.bench)
        if not _can_reader_assign_listing_date(
            request,
            assigned_bench,
            reader_group=reader_group,
        ):
            raise ValidationError({"detail": "Not authorized to submit proceedings for this case."})
        if (
            assigned_bench
            and len(tuple(assigned_bench.judge_groups or ())) > 1
            and not is_reader_date_authority_for_bench(
                assigned_bench.bench_key,
                user,
                reader_group=reader_group,
            )
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Only the primary bench reader can submit proceedings "
                        "for division-bench cases."
                    )
                }
            )

        proceeding, _ = ReaderDailyProceeding.objects.update_or_create(
            efiling=efiling,
            hearing_date=hearing_date,
            bench_key=assigned_bench.bench_key if assigned_bench else str(efiling.bench),
            defaults={
                "next_listing_date": next_listing_date,
                "proceedings_text": proceedings_text,
                "reader_remark": legacy_reader_remark or resolved_steno_remark,
                "steno_remark": resolved_steno_remark,
                "steno_purpose": steno_purpose,
                "listing_remark": listing_remark,
                "listing_sync_status": ReaderDailyProceeding.ListingSyncStatus.SYNCED,
                "submitted_by": user,
                "updated_by": user,
            },
        )

        CourtroomJudgeDecision.objects.filter(
            efiling_id=efiling_id,
            forwarded_for_date=hearing_date,
        ).update(
            listing_date=next_listing_date,
            reader_listing_remark=listing_remark or proceedings_text,
            updated_by=user,
            updated_at=timezone.now(),
        )
        try:
            apply_reader_assign_date(
                efiling_ids=[int(efiling_id)],
                forwarded_for_date=hearing_date,
                listing_date=next_listing_date,
                listing_remark=listing_remark or proceedings_text,
                assigned_by=user,
            )
        except Exception:
            logger.exception("bench workflow state submit-proceeding dual-write failed")

        _judge_user_id, steno_user_id = _resolve_judge_and_steno_for_reader_submission(
            request=request,
            efiling=efiling,
            reader_group=reader_group,
        )
        workflow, _ = StenoOrderWorkflow.objects.update_or_create(
            proceeding=proceeding,
            document_type=document_type,
            defaults={
                "efiling": efiling,
                "assigned_steno_id": steno_user_id,
                "workflow_status": StenoOrderWorkflow.WorkflowStatus.PENDING_UPLOAD,
                "judge_approval_status": StenoOrderWorkflow.JudgeApprovalStatus.PENDING,
                "updated_by": user,
            },
        )
        return Response(
            {
                "proceeding_id": proceeding.id,
                "workflow_id": workflow.id,
                "listing_sync_status": proceeding.listing_sync_status,
                "steno_workflow_status": workflow.workflow_status,
            },
            status=drf_status.HTTP_200_OK,
        )


class StenoQueueListView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user if getattr(request.user, "is_authenticated", False) else None
        if not user:
            raise ValidationError({"detail": "Authentication required."})

        hearing_date = request.GET.get("hearing_date")
        print(f"hearing_date: {hearing_date}")
        if hearing_date:
            try:
                hearing_date = timezone.datetime.fromisoformat(hearing_date).date()
            except (TypeError, ValueError):
                raise ValidationError({"hearing_date": "Invalid date format. Use YYYY-MM-DD."})
        ann_qs = JudgeDraftAnnotation.objects.filter(is_active=True).order_by("id")
        rows = (
            StenoOrderWorkflow.objects.filter(
                # assigned_steno=user,
                # is_active=True,
                proceeding__hearing_date=hearing_date,
            )
            .select_related("efiling", "proceeding", "draft_document_index")
            .select_related("proceeding__steno_purpose")
            .prefetch_related(
                Prefetch("judge_annotations", queryset=ann_qs),
                Prefetch("efiling__litigants"),
                "signature_rows",
            )
            .order_by("-updated_at", "-id")
        )
        items = []
        for row in rows:
            draft_entry = _latest_workflow_order_entry(row.efiling, row.id, "DRAFT")
            signed_entry = _latest_workflow_order_entry(row.efiling, row.id, "SIGNED_FINAL")
            draft_id = row.draft_document_index_id
            signed_id = row.signed_document_index_id
            signature_rows = list(
                row.signature_rows.values(
                    "judge_user_id",
                    "steno_user_id",
                    "signature_status",
                    "signed_at",
                )
            )
            ann_list = [
                {
                    "id": a.id,
                    "note_text": a.note_text,
                    "page_number": a.page_number,
                    "status": a.status,
                    "annotation_type": a.annotation_type,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in row.judge_annotations.all()
            ]
            petitioner_vs_respondent = (
                (row.efiling.petitioner_name or "").strip()
                or build_petitioner_vs_respondent(
                    row.efiling,
                    fallback_petitioner_name=row.efiling.petitioner_name or "",
                )
            )
            items.append(
                {
                    "workflow_id": row.id,
                    "efiling_id": row.efiling_id,
                    "assigned_steno_id": row.assigned_steno_id,
                    "is_primary_steno": row.assigned_steno_id == getattr(user, "id", None),
                    "case_number": row.efiling.case_number,
                    "e_filing_number": row.efiling.e_filing_number,
                    "petitioner_vs_respondent": petitioner_vs_respondent,
                    "document_type": row.document_type,
                    "workflow_status": row.workflow_status,
                    "judge_approval_status": row.judge_approval_status,
                    "judge_approval_notes": row.judge_approval_notes,
                    "draft_document_index_id": draft_id,
                    "draft_preview_url": (
                        _order_upload_preview_url(request, getattr(draft_entry, "upload", None))
                        or _steno_draft_preview_url(request, draft_id)
                    ),
                    "signed_document_index_id": signed_id,
                    "signed_preview_url": (
                        _order_upload_preview_url(request, getattr(signed_entry, "upload", None))
                        or _steno_signed_preview_url(request, signed_id)
                    ),
                    "draft_order_no": getattr(draft_entry, "order_no", None),
                    "signed_order_no": getattr(signed_entry, "order_no", None),
                    "draft_uploaded_at": (
                        draft_entry.timestamp.isoformat() if draft_entry and draft_entry.timestamp else None
                    ),
                    "signed_uploaded_at": (
                        signed_entry.timestamp.isoformat() if signed_entry and signed_entry.timestamp else None
                    ),
                    "signature_rows": [
                        {
                            "judge_user_id": int(sr["judge_user_id"]),
                            "steno_user_id": int(sr["steno_user_id"]),
                            "signature_status": sr["signature_status"],
                            "signed_at": sr["signed_at"].isoformat() if sr["signed_at"] else None,
                        }
                        for sr in signature_rows
                    ],
                    "all_required_signatures_done": _all_required_signatures_done(row),
                    "can_mark_signature_complete": any(
                        int(sr["steno_user_id"]) == getattr(user, "id", None)
                        and sr["signature_status"] != StenoWorkflowSignature.SignatureStatus.SIGNED
                        for sr in signature_rows
                    ),
                    "digitally_signed_at": (
                        row.digitally_signed_at.isoformat()
                        if row.digitally_signed_at
                        else None
                    ),
                    "digital_signature_provider": row.digital_signature_provider,
                    "digital_signature_certificate_serial": row.digital_signature_certificate_serial,
                    "digital_signature_signer_name": row.digital_signature_signer_name,
                    "digital_signature_reason": row.digital_signature_reason,
                    "judge_approved_at": (
                        row.judge_approved_at.isoformat() if row.judge_approved_at else None
                    ),
                    "judge_annotations": ann_list,
                    "hearing_date": row.proceeding.hearing_date.isoformat(),
                    "next_listing_date": row.proceeding.next_listing_date.isoformat(),
                    "proceedings_text": row.proceeding.proceedings_text,
                    "steno_purpose_code": row.proceeding.steno_purpose_id,
                    "steno_purpose_name": (
                        row.proceeding.steno_purpose.purpose_name
                        if row.proceeding.steno_purpose
                        else None
                    ),
                }
            )
        return Response({"items": items}, status=drf_status.HTTP_200_OK)


class StenoDraftFileUploadView(APIView):
    """Multipart PDF upload: stores draft into CIS order_details_a."""

    def post(self, request, *args, **kwargs):
        user = request.user if getattr(request.user, "is_authenticated", False) else None
        if not user:
            raise ValidationError({"detail": "Authentication required."})
        raw_wid = request.data.get("workflow_id")
        try:
            workflow_id = int(raw_wid)
        except (TypeError, ValueError):
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        upload = request.FILES.get("file")
        if not upload:
            raise ValidationError({"file": "PDF file is required."})

        workflow = (
            StenoOrderWorkflow.objects.select_related("efiling")
            .filter(id=workflow_id, is_active=True)
            .first()
        )
        if not workflow:
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        if workflow.assigned_steno_id != getattr(user, "id", None):
            raise ValidationError({"detail": "Not authorized for this workflow."})
        if workflow.workflow_status not in _STENO_UPLOAD_ALLOWED:
            raise ValidationError(
                {"detail": "Cannot upload a draft in the current workflow state."}
            )

        validate_pdf_file(upload, "file")
        if hasattr(upload, "seek"):
            upload.seek(0)
        efiling = workflow.efiling
        had_changes_requested = (
            workflow.workflow_status == StenoOrderWorkflow.WorkflowStatus.CHANGES_REQUESTED
        )

        with transaction.atomic():
            upload_url = _store_steno_order_file(
                upload=upload,
                efiling=efiling,
                workflow_id=workflow.id,
                phase="DRAFT",
            )
            order_entry = _create_order_details_a_entry(
                efiling=efiling,
                workflow_id=workflow.id,
                upload_url=upload_url,
                phase="DRAFT",
                actor_login=getattr(user, "email", None),
            )
            workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.UPLOADED_BY_STENO
            workflow.updated_by = user
            update_fields = [
                "workflow_status",
                "updated_by",
                "updated_at",
            ]
            if had_changes_requested:
                workflow.judge_approval_status = StenoOrderWorkflow.JudgeApprovalStatus.PENDING
                update_fields.append("judge_approval_status")
            workflow.save(update_fields=update_fields)

        return Response(
            {
                "workflow_status": workflow.workflow_status,
                "draft_order_no": order_entry.order_no,
                "draft_preview_url": _order_upload_preview_url(request, order_entry.upload),
            },
            status=drf_status.HTTP_200_OK,
        )


class StenoDraftUploadView(APIView):
    def post(self, request, *args, **kwargs):
        raise ValidationError(
            {
                "detail": (
                    "Link-by-document-index is disabled. "
                    "Upload draft via file upload so it is stored in order_details_a."
                )
            }
        )


class StenoSignedUploadPublishView(APIView):
    """
    Upload signed PDF after judge approval and mark workflow as published.
    """

    def post(self, request, *args, **kwargs):
        user = request.user if getattr(request.user, "is_authenticated", False) else None
        if not user:
            raise ValidationError({"detail": "Authentication required."})
        raw_wid = request.data.get("workflow_id")
        try:
            workflow_id = int(raw_wid)
        except (TypeError, ValueError):
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        upload = request.FILES.get("file")
        if not upload:
            raise ValidationError({"file": "Signed PDF file is required."})

        workflow = (
            StenoOrderWorkflow.objects.select_related("efiling")
            .filter(id=workflow_id, is_active=True)
            .first()
        )
        if not workflow:
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        if workflow.assigned_steno_id != getattr(user, "id", None):
            raise ValidationError({"detail": "Not authorized for this workflow."})
        if _primary_steno_user_id_for_workflow(workflow) != getattr(user, "id", None):
            raise ValidationError({"detail": "Only primary steno can publish final order."})
        if workflow.workflow_status != StenoOrderWorkflow.WorkflowStatus.JUDGE_APPROVED:
            if workflow.workflow_status not in (
                StenoOrderWorkflow.WorkflowStatus.SHARED_FOR_SIGNATURE,
                StenoOrderWorkflow.WorkflowStatus.SIGNATURES_IN_PROGRESS,
            ):
                raise ValidationError(
                    {"detail": "Signed publish is allowed only after judge approval."}
                )
        if workflow.judge_approval_status != StenoOrderWorkflow.JudgeApprovalStatus.APPROVED:
            raise ValidationError({"detail": "Judge approval is required before publish."})
        draft_entry = _latest_workflow_order_entry(workflow.efiling, workflow.id, "DRAFT")
        if not draft_entry:
            raise ValidationError({"detail": "Draft document missing for this workflow."})
        if not _all_required_signatures_done(workflow):
            raise ValidationError({"detail": "All required judge signatures are not complete yet."})

        validate_pdf_file(upload, "file")
        if hasattr(upload, "seek"):
            upload.seek(0)
        efiling = workflow.efiling
        with transaction.atomic():
            upload_url = _store_steno_order_file(
                upload=upload,
                efiling=efiling,
                workflow_id=workflow.id,
                phase="SIGNED_FINAL",
            )
            order_entry = _create_order_details_a_entry(
                efiling=efiling,
                workflow_id=workflow.id,
                upload_url=upload_url,
                phase="SIGNED_FINAL",
                actor_login=getattr(user, "email", None),
            )
            workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.SIGNED_AND_PUBLISHED
            workflow.digitally_signed_by = user
            workflow.digitally_signed_at = timezone.now()
            workflow.digital_signature_metadata = {
                "order_details_a": {
                    "cino": order_entry.cino,
                    "order_no": order_entry.order_no,
                },
                "captured_at": timezone.now().isoformat(),
            }
            workflow.published_at = timezone.now()
            workflow.updated_by = user
            workflow.save(
                update_fields=[
                    "workflow_status",
                    "digitally_signed_by",
                    "digitally_signed_at",
                    "digital_signature_metadata",
                    "published_at",
                    "updated_by",
                    "updated_at",
                ]
            )
        return Response(
            {
                "workflow_status": workflow.workflow_status,
                "signed_order_no": order_entry.order_no,
                "signed_preview_url": _order_upload_preview_url(request, order_entry.upload),
                "digitally_signed_at": workflow.digitally_signed_at.isoformat()
                if workflow.digitally_signed_at
                else None,
                "published_at": workflow.published_at.isoformat()
                if workflow.published_at
                else None,
            },
            status=drf_status.HTTP_200_OK,
        )


class StenoShareApprovedDraftView(APIView):
    def post(self, request, *args, **kwargs):
        payload = StenoShareForSignatureSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        user = request.user if getattr(request.user, "is_authenticated", False) else None
        workflow = (
            StenoOrderWorkflow.objects.select_related("efiling")
            .filter(id=payload.validated_data["workflow_id"], is_active=True)
            .first()
        )
        if not workflow:
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        if _primary_steno_user_id_for_workflow(workflow) != getattr(user, "id", None):
            raise ValidationError({"detail": "Only primary steno can share approved draft."})
        if workflow.workflow_status != StenoOrderWorkflow.WorkflowStatus.JUDGE_APPROVED:
            raise ValidationError({"detail": "Draft can be shared only after judge approval."})

        required_judges = _required_judge_user_ids_for_workflow(workflow)
        if len(required_judges) <= 1:
            return Response(
                {"detail": "Single-judge bench does not require steno sharing."},
                status=drf_status.HTTP_200_OK,
            )
        bench_key = (
            get_bench_configuration_for_stored_value(getattr(workflow.efiling, "bench", None)).bench_key
            if get_bench_configuration_for_stored_value(getattr(workflow.efiling, "bench", None))
            else None
        )
        created = 0
        for judge_user_id in required_judges:
            judge_t = JudgeT.objects.filter(user_id=judge_user_id).first()
            if not judge_t:
                continue
            mapping_qs = JudgeStenoMapping.objects.filter(judge_id=judge_t.id, is_active=True)
            if bench_key:
                mapping_qs = mapping_qs.filter(Q(bench_key=bench_key) | Q(bench_key__isnull=True))
            mapping = mapping_qs.order_by("-effective_from", "-id").first()
            if not mapping:
                continue
            _, was_created = StenoWorkflowSignature.objects.get_or_create(
                workflow=workflow,
                judge_user_id=judge_user_id,
                defaults={
                    "steno_user_id": mapping.steno_user_id,
                    "signature_status": StenoWorkflowSignature.SignatureStatus.PENDING,
                },
            )
            if was_created:
                created += 1
        workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.SHARED_FOR_SIGNATURE
        workflow.updated_by = user
        workflow.save(update_fields=["workflow_status", "updated_by", "updated_at"])
        return Response(
            {"workflow_status": workflow.workflow_status, "signature_rows_created": created},
            status=drf_status.HTTP_200_OK,
        )


class StenoMarkSignatureCompleteView(APIView):
    def post(self, request, *args, **kwargs):
        payload = StenoMarkSignatureSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        user = request.user if getattr(request.user, "is_authenticated", False) else None
        workflow = StenoOrderWorkflow.objects.filter(
            id=payload.validated_data["workflow_id"], is_active=True
        ).first()
        if not workflow:
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        row = StenoWorkflowSignature.objects.filter(
            workflow=workflow,
            steno_user=user,
            is_active=True,
        ).first()
        if not row:
            raise ValidationError({"detail": "No signature assignment found for this steno/workflow."})
        row.signature_status = StenoWorkflowSignature.SignatureStatus.SIGNED
        row.signed_at = timezone.now()
        row.updated_by = user
        row.save(update_fields=["signature_status", "signed_at", "updated_by", "updated_at"])
        if workflow.workflow_status == StenoOrderWorkflow.WorkflowStatus.SHARED_FOR_SIGNATURE:
            workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.SIGNATURES_IN_PROGRESS
            workflow.updated_by = user
            workflow.save(update_fields=["workflow_status", "updated_by", "updated_at"])
        return Response(
            {
                "workflow_status": workflow.workflow_status,
                "all_required_signatures_done": _all_required_signatures_done(workflow),
            },
            status=drf_status.HTTP_200_OK,
        )


class StenoSubmitForJudgeApprovalView(APIView):
    def post(self, request, *args, **kwargs):
        payload = StenoSubmitForJudgeSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        user = request.user if getattr(request.user, "is_authenticated", False) else None
        workflow = StenoOrderWorkflow.objects.filter(
            id=payload.validated_data["workflow_id"],
            is_active=True,
        ).first()
        if not workflow:
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        if workflow.assigned_steno_id != getattr(user, "id", None):
            raise ValidationError({"detail": "Not authorized for this workflow."})
        draft_entry = _latest_workflow_order_entry(workflow.efiling, workflow.id, "DRAFT")
        if not draft_entry:
            raise ValidationError({"detail": "Upload draft document before sending to judge."})
        workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.SENT_FOR_JUDGE_APPROVAL
        workflow.updated_by = user
        workflow.save(update_fields=["workflow_status", "updated_by", "updated_at"])
        return Response({"workflow_status": workflow.workflow_status}, status=drf_status.HTTP_200_OK)
