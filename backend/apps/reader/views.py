from __future__ import annotations

from typing import List
from datetime import date as date_type

from django.db.models import Prefetch
from django.db.models import Q
from django.utils import timezone
from rest_framework import status as drf_status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Efiling, EfilingCaseDetails, EfilingDocumentsIndex
from apps.core.models import ReaderJudgeAssignment, JudgeT
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
)
from apps.efiling.party_display import build_petitioner_vs_respondent
from apps.judge.models import (
    CourtroomDecisionRequestedDocument,
    CourtroomJudgeDecision,
    JudgeStenoMapping,
)
from apps.judge.courtroom_approval import (
    efiling_ids_with_all_required_approvals,
    legacy_role_from_user_for_bench,
)
from .models import CourtroomForward, CourtroomForwardDocument, ReaderDailyProceeding, StenoOrderWorkflow
from .serializers import (
    CourtroomForwardSerializer,
    AssignBenchesSerializer,
    ReaderDailyProceedingSubmitSerializer,
    StenoDraftUploadSerializer,
    StenoSubmitForJudgeSerializer,
    StenoResolveAnnotationSerializer,
)


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
    if allowed_bench_keys:
        filter_q |= Q(bench__in=allowed_bench_keys)
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
) -> bool:
    forward_groups = set(get_required_judge_groups(forward.bench_key))
    bench_groups = set(bench_config.judge_groups)
    return bool(forward_groups) and forward_groups.issubset(bench_groups)


def _get_relevant_forwards_for_bench(
    forwards: list[CourtroomForward],
    bench_config,
) -> list[CourtroomForward]:
    return [
        forward
        for forward in forwards
        if _is_forward_relevant_to_bench(forward, bench_config)
    ]


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
            items.append({
                'bench_key': bench.bench_key,
                'label': bench.label,
                'bench_code': bench.bench_code,
                'bench_name': bench.bench_name,
                'judge_names': list(bench.judge_names),
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
                req = tuple(get_required_judge_groups(fwd.bench_key)) if fwd else tuple()
                grp = d.bench_role_group or (
                    legacy_role_from_user_for_bench(d.judge_user, req) if req else None
                )
                if not grp:
                    continue
                if key not in decision_map:
                    decision_map[key] = {}
                    decision_status_map[key] = {}
                decision_map[key][grp] = bool(d.approved)
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
            if assigned_bench:
                relevant_forwards = _get_relevant_forwards_for_bench(
                    forwards_by_efiling.get(e.id, []),
                    assigned_bench,
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
    judge_ids = []
    if assigned_bench:
        judge_ids = list(assigned_bench.judge_user_ids or [])
    if not judge_ids:
        judge_ids = list(
            ReaderJudgeAssignment.objects.filter(
                reader_user=acting_user,
                effective_to__isnull=True,
            ).values_list("judge__user_id", flat=True)
        )

    judge_user_id = judge_ids[0] if judge_ids else None
    if not judge_user_id:
        return (None, None)

    mapping_qs = JudgeStenoMapping.objects.filter(
        judge_user_id=judge_user_id,
        is_active=True,
    )
    if bench_key:
        mapping_qs = mapping_qs.filter(Q(bench_key=bench_key) | Q(bench_key__isnull=True))
    steno_mapping = mapping_qs.order_by("-effective_from", "-id").first()
    return (judge_user_id, steno_mapping.steno_user_id if steno_mapping else None)


class ReaderDailyProceedingsListView(APIView):
    def get(self, request, *args, **kwargs):
        reader_group = request.query_params.get("reader_group")
        page_size_raw = request.query_params.get("page_size")
        page_size = int(page_size_raw) if page_size_raw not in (None, "", "null") else 200

        allowed_bench_filter = _get_reader_allowed_efiling_bench_filter(
            request,
            reader_group=reader_group,
        )
        heard_ids = set(
            CourtroomJudgeDecision.objects.values_list("efiling_id", flat=True).distinct()
        )
        qs = Efiling.objects.filter(
            id__in=heard_ids,
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
        rows = (
            StenoOrderWorkflow.objects.filter(
                assigned_steno=user,
                is_active=True,
            )
            .select_related("efiling", "proceeding")
            .order_by("-updated_at", "-id")
        )
        items = []
        for row in rows:
            items.append(
                {
                    "workflow_id": row.id,
                    "efiling_id": row.efiling_id,
                    "case_number": row.efiling.case_number,
                    "e_filing_number": row.efiling.e_filing_number,
                    "document_type": row.document_type,
                    "workflow_status": row.workflow_status,
                    "judge_approval_status": row.judge_approval_status,
                    "judge_approval_notes": row.judge_approval_notes,
                    "hearing_date": row.proceeding.hearing_date.isoformat(),
                    "next_listing_date": row.proceeding.next_listing_date.isoformat(),
                    "proceedings_text": row.proceeding.proceedings_text,
                }
            )
        return Response({"items": items}, status=drf_status.HTTP_200_OK)


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
        draft_id = payload.validated_data["draft_document_index_id"]
        if not EfilingDocumentsIndex.objects.filter(
            id=draft_id, document__e_filing_id=workflow.efiling_id
        ).exists():
            raise ValidationError({"draft_document_index_id": "Invalid draft document for case."})
        workflow.draft_document_index_id = draft_id
        workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.UPLOADED_BY_STENO
        workflow.updated_by = user
        workflow.save(
            update_fields=["draft_document_index", "workflow_status", "updated_by", "updated_at"]
        )
        return Response({"workflow_status": workflow.workflow_status}, status=drf_status.HTTP_200_OK)


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
