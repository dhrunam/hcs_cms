from __future__ import annotations

from typing import List
from datetime import date as date_type
import logging

from django.db import transaction
from django.db.models import Prefetch
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from rest_framework import status as drf_status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Efiling, EfilingCaseDetails, EfilingDocuments, EfilingDocumentsIndex
from apps.core.models import ReaderJudgeAssignment, JudgeT
from apps.core.bench_config import (
    BENCH_TOKEN_TO_JUDGE_GROUP,
    LEGACY_READER_GROUP_TO_TOKENS,
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
)
from apps.efiling.party_display import build_petitioner_vs_respondent
from apps.efiling.pdf_validators import validate_pdf_file
from apps.efiling.review_utils import create_scrutiny_history
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
    StenoOrderWorkflow,
)
from .workflow_state import (
    apply_reader_assign_date,
    upsert_state_on_forward,
)
from .serializers import (
    CourtroomForwardSerializer,
    AssignBenchesSerializer,
    ReaderDailyProceedingSubmitSerializer,
    StenoDraftUploadSerializer,
    StenoSubmitForJudgeSerializer,
    StenoResolveAnnotationSerializer,
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


_STENO_UPLOAD_ALLOWED = frozenset(
    {
        StenoOrderWorkflow.WorkflowStatus.PENDING_UPLOAD,
        StenoOrderWorkflow.WorkflowStatus.UPLOADED_BY_STENO,
        StenoOrderWorkflow.WorkflowStatus.CHANGES_REQUESTED,
    }
)
logger = logging.getLogger(__name__)


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


def _bench_filter_for_configuration(bench_config) -> Q:
    filter_q = Q(bench=bench_config.bench_key)
    if bench_config.bench_code:
        filter_q |= Q(bench=bench_config.bench_code)
    return filter_q


def _is_forward_relevant_to_bench(
    forward: CourtroomForward,
    bench_config,
    reader_slot_group: str | None = None,
) -> bool:
    if reader_slot_group:
        forward_groups = tuple(get_required_judge_groups(forward.bench_key))
        return len(forward_groups) == 1 and forward_groups[0] == reader_slot_group
    forward_groups = set(get_required_judge_groups(forward.bench_key))
    bench_groups = set(bench_config.judge_groups)
    return bool(forward_groups) and forward_groups.issubset(bench_groups)


def _get_relevant_forwards_for_bench(
    forwards: list[CourtroomForward],
    bench_config,
    reader_slot_group: str | None = None,
) -> list[CourtroomForward]:
    return [
        forward
        for forward in forwards
        if _is_forward_relevant_to_bench(
            forward,
            bench_config,
            reader_slot_group=reader_slot_group,
        )
    ]


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
    if reader_group:
        for token in LEGACY_READER_GROUP_TO_TOKENS.get(reader_group, set()):
            group_name = BENCH_TOKEN_TO_JUDGE_GROUP.get(token)
            if group_name and group_name in set(bench_config.judge_groups):
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

    return {
        "approval_status": approval_status,
        "approval_notes": approval_notes,
        "approval_listing_date": approval_listing_date,
        "requested_documents": requested_documents,
        "approval_bench_key": approval_bench_key,
        "approval_forwarded_for_date": approval_forwarded_for_date,
        "listing_summary": listing_summary,
    }


def _get_effective_forwarded_for_date(
    *,
    efiling: Efiling,
    requested_forwarded_for_date,
) -> date_type:
    assigned_bench = get_bench_configuration_for_stored_value(efiling.bench)
    if not assigned_bench:
        return requested_forwarded_for_date

    existing_forwards = list(
        CourtroomForward.objects.filter(efiling_id=efiling.id)
        .order_by("-forwarded_for_date", "-id")
        .all()
    )
    relevant_forwards = _get_relevant_forwards_for_bench(
        existing_forwards,
        assigned_bench,
    )
    for forward in relevant_forwards:
        has_listing_date = CourtroomJudgeDecision.objects.filter(
            efiling_id=efiling.id,
            forwarded_for_date=forward.forwarded_for_date,
            listing_date__isnull=False,
        ).exists()
        if not has_listing_date:
            return forward.forwarded_for_date

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
                        label = str(grp).replace("JUDGE_", "Judge ")
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
                    label = grp.replace("JUDGE_", "Judge ")
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
                # Full bench-relevant forwards are used for final approval aggregation.
                relevant_forwards = _get_relevant_forwards_for_bench(
                    forwards_by_efiling.get(e.id, []),
                    assigned_bench,
                )
                # Reader-slot forwards are used to determine if this reader has forwarded yet.
                reader_slot_forwards = _get_relevant_forwards_for_bench(
                    forwards_by_efiling.get(e.id, []),
                    assigned_bench,
                    reader_slot_group=reader_slot_group,
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
            if assigned_bench and not reader_slot_forwards and approval_status != "NOT_FORWARDED":
                # Enforce per-reader forward scope in dashboard status progression.
                approval_status = "NOT_FORWARDED"
                approval_notes = []
                approval_listing_date = None
                requested_documents = []
                approval_forwarded_for_date = None

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
                "approval_notes": approval_notes,
                "approval_bench_key": approval_bench_key,
                "approval_forwarded_for_date": approval_forwarded_for_date,
                "approval_listing_date": approval_listing_date,
                "listing_summary": approval_state["listing_summary"],
                "requested_documents": requested_documents,
                "can_assign_listing_date": can_assign_listing_date,
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
                e.bench = bench_config.bench_code or bench_key
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
        
        try:
            efiling = Efiling.objects.get(id=efiling_id)
        except Efiling.DoesNotExist:
            return Response({"detail": "Not found."}, status=drf_status.HTTP_404_NOT_FOUND)

        CourtroomForward.objects.filter(efiling_id=efiling_id).delete()
        CourtroomJudgeDecision.objects.filter(efiling_id=efiling_id).delete()
            
        efiling.bench = None
        efiling.save(update_fields=["bench"])
        
        return Response({"detail": "Bench reset successful. Case returned to Scrutiny pool."}, status=drf_status.HTTP_200_OK)


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
        for row in ReaderDailyProceeding.objects.filter(efiling_id__in=ids).order_by(
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
        reader_remark = payload.validated_data.get("reader_remark")
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

        proceeding, _ = ReaderDailyProceeding.objects.update_or_create(
            efiling=efiling,
            hearing_date=hearing_date,
            bench_key=assigned_bench.bench_key if assigned_bench else str(efiling.bench),
            defaults={
                "next_listing_date": next_listing_date,
                "proceedings_text": proceedings_text,
                "reader_remark": reader_remark,
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
            reader_listing_remark=reader_remark or proceedings_text,
            updated_by=user,
            updated_at=timezone.now(),
        )
        try:
            apply_reader_assign_date(
                efiling_ids=[int(efiling_id)],
                forwarded_for_date=hearing_date,
                listing_date=next_listing_date,
                listing_remark=reader_remark or proceedings_text,
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
        ann_qs = JudgeDraftAnnotation.objects.filter(is_active=True).order_by("id")
        rows = (
            StenoOrderWorkflow.objects.filter(
                assigned_steno=user,
                is_active=True,
            )
            .select_related("efiling", "proceeding", "draft_document_index")
            .prefetch_related(
                Prefetch("judge_annotations", queryset=ann_qs),
                Prefetch("efiling__litigants"),
            )
            .order_by("-updated_at", "-id")
        )
        items = []
        for row in rows:
            draft_id = row.draft_document_index_id
            signed_id = row.signed_document_index_id
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
                    "case_number": row.efiling.case_number,
                    "e_filing_number": row.efiling.e_filing_number,
                    "petitioner_vs_respondent": petitioner_vs_respondent,
                    "document_type": row.document_type,
                    "workflow_status": row.workflow_status,
                    "judge_approval_status": row.judge_approval_status,
                    "judge_approval_notes": row.judge_approval_notes,
                    "draft_document_index_id": draft_id,
                    "draft_preview_url": _steno_draft_preview_url(request, draft_id),
                    "signed_document_index_id": signed_id,
                    "signed_preview_url": _steno_signed_preview_url(request, signed_id),
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
                }
            )
        return Response({"items": items}, status=drf_status.HTTP_200_OK)


class StenoDraftFileUploadView(APIView):
    """Multipart PDF upload: creates EfilingDocumentsIndex on the case and links workflow."""

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
        signature_provider = str(request.data.get("signature_provider") or "").strip() or None
        signature_serial = str(request.data.get("certificate_serial") or "").strip() or None
        signature_signer = str(request.data.get("signer_name") or "").strip() or None
        signature_reason = str(request.data.get("signature_reason") or "").strip() or None
        signature_txn = str(request.data.get("signature_txn_id") or "").strip() or None

        efiling = workflow.efiling
        had_changes_requested = (
            workflow.workflow_status == StenoOrderWorkflow.WorkflowStatus.CHANGES_REQUESTED
        )

        with transaction.atomic():
            doc_parent, _ = EfilingDocuments.objects.get_or_create(
                e_filing=efiling,
                document_type=f"STENO_WF_{workflow.id}",
                defaults={
                    "e_filing_number": efiling.e_filing_number,
                    "is_ia": False,
                },
            )
            last_sequence = (
                EfilingDocumentsIndex.objects.filter(document__e_filing=efiling)
                .exclude(document_sequence__isnull=True)
                .order_by("-document_sequence")
                .values_list("document_sequence", flat=True)
                .first()
            )
            next_sequence = (last_sequence or 0) + 1
            index = EfilingDocumentsIndex.objects.create(
                document=doc_parent,
                document_part_name=f"Steno draft wf{workflow.id} seq{next_sequence}",
                file_part_path=upload,
                document_sequence=next_sequence,
                scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
                is_new_for_scrutiny=False,
                created_by=user,
                updated_by=user,
                comments="Steno draft",
            )
            create_scrutiny_history(
                index,
                comments="Steno draft uploaded.",
                user=user,
                scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            )

            workflow.draft_document_index = index
            workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.UPLOADED_BY_STENO
            workflow.updated_by = user
            update_fields = [
                "draft_document_index",
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
                "draft_document_index_id": index.id,
                "draft_preview_url": _steno_draft_preview_url(request, index.id),
            },
            status=drf_status.HTTP_200_OK,
        )


class StenoDraftUploadView(APIView):
    def post(self, request, *args, **kwargs):
        payload = StenoDraftUploadSerializer(data=request.data)
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
        if workflow.workflow_status not in _STENO_UPLOAD_ALLOWED:
            raise ValidationError(
                {"detail": "Cannot link a draft in the current workflow state."}
            )
        draft_id = payload.validated_data["draft_document_index_id"]
        if not EfilingDocumentsIndex.objects.filter(
            id=draft_id, document__e_filing_id=workflow.efiling_id
        ).exists():
            raise ValidationError({"draft_document_index_id": "Invalid draft document for case."})
        had_changes_requested = (
            workflow.workflow_status == StenoOrderWorkflow.WorkflowStatus.CHANGES_REQUESTED
        )
        workflow.draft_document_index_id = draft_id
        workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.UPLOADED_BY_STENO
        workflow.updated_by = user
        save_fields = ["draft_document_index", "workflow_status", "updated_by", "updated_at"]
        if had_changes_requested:
            workflow.judge_approval_status = StenoOrderWorkflow.JudgeApprovalStatus.PENDING
            save_fields.append("judge_approval_status")
        workflow.save(update_fields=save_fields)
        return Response({"workflow_status": workflow.workflow_status}, status=drf_status.HTTP_200_OK)


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
        if workflow.workflow_status != StenoOrderWorkflow.WorkflowStatus.JUDGE_APPROVED:
            raise ValidationError(
                {"detail": "Signed publish is allowed only after judge approval."}
            )
        if workflow.judge_approval_status != StenoOrderWorkflow.JudgeApprovalStatus.APPROVED:
            raise ValidationError({"detail": "Judge approval is required before publish."})
        if not workflow.draft_document_index_id:
            raise ValidationError({"detail": "Draft document missing for this workflow."})

        validate_pdf_file(upload, "file")
        if hasattr(upload, "seek"):
            upload.seek(0)
        signature_provider = str(request.data.get("signature_provider") or "").strip() or None
        signature_serial = str(request.data.get("certificate_serial") or "").strip() or None
        signature_signer = str(request.data.get("signer_name") or "").strip() or None
        signature_reason = str(request.data.get("signature_reason") or "").strip() or None
        signature_txn = str(request.data.get("signature_txn_id") or "").strip() or None

        efiling = workflow.efiling
        with transaction.atomic():
            doc_parent, _ = EfilingDocuments.objects.get_or_create(
                e_filing=efiling,
                document_type=f"STENO_SIGNED_WF_{workflow.id}",
                defaults={
                    "e_filing_number": efiling.e_filing_number,
                    "is_ia": False,
                },
            )
            last_sequence = (
                EfilingDocumentsIndex.objects.filter(document__e_filing=efiling)
                .exclude(document_sequence__isnull=True)
                .order_by("-document_sequence")
                .values_list("document_sequence", flat=True)
                .first()
            )
            next_sequence = (last_sequence or 0) + 1
            index = EfilingDocumentsIndex.objects.create(
                document=doc_parent,
                document_part_name=f"Steno signed wf{workflow.id} seq{next_sequence}",
                file_part_path=upload,
                document_sequence=next_sequence,
                scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
                is_new_for_scrutiny=False,
                created_by=user,
                updated_by=user,
                comments="Steno signed order",
            )
            create_scrutiny_history(
                index,
                comments="Steno uploaded signed order and published.",
                user=user,
                scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            )
            workflow.signed_document_index = index
            workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.SIGNED_AND_PUBLISHED
            workflow.digitally_signed_by = user
            workflow.digitally_signed_at = timezone.now()
            workflow.digital_signature_provider = signature_provider
            workflow.digital_signature_certificate_serial = signature_serial
            workflow.digital_signature_signer_name = signature_signer
            workflow.digital_signature_reason = signature_reason
            workflow.digital_signature_metadata = {
                "signature_txn_id": signature_txn,
                "captured_at": timezone.now().isoformat(),
            }
            workflow.published_at = timezone.now()
            workflow.updated_by = user
            workflow.save(
                update_fields=[
                    "signed_document_index",
                    "workflow_status",
                    "digitally_signed_by",
                    "digitally_signed_at",
                    "digital_signature_provider",
                    "digital_signature_certificate_serial",
                    "digital_signature_signer_name",
                    "digital_signature_reason",
                    "digital_signature_metadata",
                    "published_at",
                    "updated_by",
                    "updated_at",
                ]
            )
        return Response(
            {
                "workflow_status": workflow.workflow_status,
                "signed_document_index_id": index.id,
                "signed_preview_url": _steno_signed_preview_url(request, index.id),
                "digitally_signed_at": workflow.digitally_signed_at.isoformat()
                if workflow.digitally_signed_at
                else None,
                "published_at": workflow.published_at.isoformat()
                if workflow.published_at
                else None,
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
        if not workflow.draft_document_index_id:
            raise ValidationError({"detail": "Upload draft document before sending to judge."})
        workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.SENT_FOR_JUDGE_APPROVAL
        workflow.updated_by = user
        workflow.save(update_fields=["workflow_status", "updated_by", "updated_at"])
        return Response({"workflow_status": workflow.workflow_status}, status=drf_status.HTTP_200_OK)
