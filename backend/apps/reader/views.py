from __future__ import annotations

from typing import Dict, List, Sequence, Set, Any
from datetime import date as date_type

from django.db import transaction
from django.db.models import Prefetch, Q
from django.utils import timezone
from rest_framework import status as drf_status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.core.models import Efiling, EfilingCaseDetails, EfilingDocumentsIndex
from apps.efiling.party_display import build_petitioner_vs_respondent
from apps.judge.models import (
    CourtroomDecisionRequestedDocument,
    CourtroomJudgeDecision,
)
from apps.listing.models import CauseList, CauseListEntry
from .models import CourtroomForward, CourtroomForwardDocument
from .serializers import (
    CourtroomForwardSerializer,
    AssignBenchesSerializer,
)

BENCH_TO_REQUIRED_GROUPS: Dict[str, Sequence[str]] = {
    "CJ": ("JUDGE_CJ",),
    "Judge1": ("JUDGE_J1",),
    "Judge2": ("JUDGE_J2",),
    "CJ+Judge1": ("JUDGE_CJ", "JUDGE_J1"),
    "CJ+Judge2": ("JUDGE_CJ", "JUDGE_J2"),
    "Judge1+Judge2": ("JUDGE_J1", "JUDGE_J2"),
    "CJ+Judge1+Judge2": ("JUDGE_CJ", "JUDGE_J1", "JUDGE_J2"),
}

def _get_reader_bench_filter(user: User, field_name: str = "bench", mock_group: str | None = None) -> Q:
    # Use real group if authenticated, or mock_group if not
    is_reader_cj = False
    is_reader_j1 = False
    is_reader_j2 = False

    if user.is_authenticated:
        # Check if user is a Reader
        reader_groups = ["READER_CJ", "READER_J1", "READER_J2"]
        is_reader_cj = user.groups.filter(name="READER_CJ").exists()
        is_reader_j1 = user.groups.filter(name="READER_J1").exists()
        is_reader_j2 = user.groups.filter(name="READER_J2").exists()

    # IF mock_group is provided (dev), it overrides or complements
    if mock_group:
        if mock_group == "READER_CJ": is_reader_cj = True
        elif mock_group == "READER_J1": is_reader_j1 = True
        elif mock_group == "READER_J2": is_reader_j2 = True

    if not (is_reader_cj or is_reader_j1 or is_reader_j2):
        # If neither authenticated nor mock_group has a specific reader role, return everything
        # to prevent "no cases found" during local testing.
        return Q()

    q_filter = Q()
    if is_reader_cj:
        q_filter |= Q(**{f"{field_name}__icontains": "CJ"})
    if is_reader_j1:
        q_filter |= Q(**{f"{field_name}__icontains": "Judge1"})
    if is_reader_j2:
        q_filter |= Q(**{f"{field_name}__icontains": "Judge2"})
    return q_filter


def _bench_required_groups(bench_key: str) -> Sequence[str]:
    req = BENCH_TO_REQUIRED_GROUPS.get(bench_key)
    if not req:
        raise ValidationError({"bench_key": f"Unknown bench_key={bench_key}."})
    return req

class RegisteredCasesListView(APIView):
    """
    Reader: show scrutiny-completed (registered) cases.
    Identical to the previous Listing Officer view but now under Reader.
    """

    def get(self, request, *args, **kwargs):
        page_size_raw = request.query_params.get("page_size")
        page_size = int(page_size_raw) if page_size_raw not in (None, "", "null") else 200

        qs = Efiling.objects.filter(is_draft=False, status="ACCEPTED").order_by("-id")
        
        # FILTER BY READER ROLE
        mock_group = request.query_params.get("reader_group")
        q_filter = _get_reader_bench_filter(request.user, mock_group=mock_group)
        if q_filter:
            qs = qs.filter(q_filter)

        total = qs.count()

        case_details_qs = EfilingCaseDetails.objects.select_related("dispute_state", "dispute_district").order_by("id")
        qs = qs.prefetch_related(
            Prefetch("litigants"),
            Prefetch("case_details", queryset=case_details_qs),
        )

        efilings = list(qs[:page_size])
        efiling_ids = [e.id for e in efilings]

        latest_forward_by_efiling: dict[int, CourtroomForward] = {}
        forwards = (
            CourtroomForward.objects.filter(efiling_id__in=efiling_ids)
            .order_by("efiling_id", "-forwarded_for_date", "-id")
            .all()
        )
        for f in forwards:
            if f.efiling_id not in latest_forward_by_efiling:
                latest_forward_by_efiling[f.efiling_id] = f

        forward_keys = {(f.efiling_id, f.forwarded_for_date) for f in latest_forward_by_efiling.values()}
        decision_map: dict[tuple[int, date_type], dict[str, bool]] = {}
        decision_status_map: dict[tuple[int, date_type], dict[str, str]] = {}
        decision_notes_map: dict[tuple[int, date_type], List[str]] = {}
        decision_listing_date_map: dict[tuple[int, date_type], List[str]] = {}
        requested_docs_map: dict[tuple[int, date_type], List[dict]] = {}

        if forward_keys:
            e_ids = sorted({eid for eid, _ in forward_keys})
            f_dates = sorted({fdate for _, fdate in forward_keys})
            decisions = (
                CourtroomJudgeDecision.objects.filter(
                    efiling_id__in=e_ids,
                    forwarded_for_date__in=f_dates,
                )
                .values(
                    "id",
                    "efiling_id",
                    "forwarded_for_date",
                    "status",
                    "approved",
                    "listing_date",
                    "decision_notes",
                    "judge_user__groups__name",
                )
                .all()
            )
            decision_ids = [int(d["id"]) for d in decisions]
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
            
            for d in decisions:
                key = (int(d["efiling_id"]), d["forwarded_for_date"])
                grp = str(d.get("judge_user__groups__name") or "")
                if key not in decision_map:
                    decision_map[key] = {}
                    decision_status_map[key] = {}
                if grp:
                    decision_map[key][grp] = bool(d.get("approved"))
                    decision_status_map[key][grp] = str(d.get("status") or "")
                
                note = (d.get("decision_notes") or "").strip()
                if note:
                    if key not in decision_notes_map: decision_notes_map[key] = []
                    label = grp.replace("JUDGE_", "Judge ") if grp else "Judge"
                    decision_notes_map[key].append(f"{label}: {note}")
                
                lst_date = d.get("listing_date")
                if lst_date:
                    decision_listing_date_map.setdefault(key, []).append(str(lst_date))
                
                decision_docs = docs_by_decision.get(int(d["id"]), [])
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
            
            latest_forward = latest_forward_by_efiling.get(e.id)
            if latest_forward:
                approval_bench_key = latest_forward.bench_key
                approval_forwarded_for_date = latest_forward.forwarded_for_date.isoformat()
                req_groups = BENCH_TO_REQUIRED_GROUPS.get(latest_forward.bench_key, ())
                key = (e.id, latest_forward.forwarded_for_date)
                group_decisions = decision_map.get(key, {})
                group_statuses = decision_status_map.get(key, {})
                approval_notes = decision_notes_map.get(key, [])
                listing_dates = decision_listing_date_map.get(key, [])
                if listing_dates:
                    approval_listing_date = sorted(listing_dates)[0]
                requested_documents = requested_docs_map.get(key, [])

                rejected = any(group_decisions.get(g) is False for g in req_groups if g in group_decisions)
                approved_all = bool(req_groups) and all(group_decisions.get(g) is True for g in req_groups)
                requested_docs = any(group_statuses.get(g) == 'REQUESTED_DOCS' for g in req_groups if g in group_statuses)
                
                if requested_docs: approval_status = "REQUESTED_DOCS"
                elif rejected: approval_status = "REJECTED"
                elif approved_all: approval_status = "APPROVED"
                else: approval_status = "PENDING"

            items.append({
                "efiling_id": e.id,
                "case_number": e.case_number,
                "e_filing_number": e.e_filing_number,
                "bench": e.bench,
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
                "listing_summary": latest_forward.listing_summary if latest_forward else None,
                "requested_documents": requested_documents,
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
        ef_qs = Efiling.objects.filter(id__in=assign_map.keys(), is_draft=False, status="ACCEPTED")
        ef_by_id = {e.id: e for e in ef_qs}

        updated_instances = []
        for eid, bench_key in assign_map.items():
            if eid in ef_by_id:
                e = ef_by_id[eid]
                e.bench = bench_key
                updated_instances.append(e)

        Efiling.objects.bulk_update(updated_instances, ["bench"])
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
        
        # Security: check if user can forward these efilings
        q_filter = _get_reader_bench_filter(request.user)
        if q_filter and efiling_ids:
            allowed_ids = list(Efiling.objects.filter(q_filter, id__in=efiling_ids).values_list("id", flat=True))
            if len(allowed_ids) != len(efiling_ids):
                raise ValidationError("You do not have permission to forward some of these cases.")

        updated = 0
        for eid in efiling_ids:
            obj, _ = CourtroomForward.objects.update_or_create(
                efiling_id=eid,
                forwarded_for_date=forwarded_for_date,
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
        required_groups = _bench_required_groups(bench_key)
        
        forwarded_efiling_ids = CourtroomForward.objects.filter(
            bench_key=bench_key, forwarded_for_date=fwd_date
        )

        # FILTER BY READER ROLE
        mock_group = request.query_params.get("reader_group")
        q_filter = _get_reader_bench_filter(request.user, field_name="bench_key", mock_group=mock_group)
        if q_filter:
            forwarded_efiling_ids = forwarded_efiling_ids.filter(q_filter)

        forwarded_efiling_ids = forwarded_efiling_ids.values_list("efiling_id", flat=True)

        approved_efiling_ids = []
        for eid in forwarded_efiling_ids:
            group_approvals = []
            for g in required_groups:
                has_approval = CourtroomJudgeDecision.objects.filter(
                    efiling_id=eid, forwarded_for_date=fwd_date,
                    judge_user__groups__name=g, approved=True
                ).exists()
                group_approvals.append(has_approval)
            
            if all(group_approvals):
                has_date = CourtroomJudgeDecision.objects.filter(
                    efiling_id=eid, forwarded_for_date=fwd_date,
                    listing_date__isnull=False
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

        if not efiling_ids or not ldate or not fwd_date:
            raise ValidationError({"efiling_ids": "Required.", "listing_date": "Required.", "forwarded_for_date": "Required."})

        # Security: check if user can assign dates to these efilings
        q_filter = _get_reader_bench_filter(request.user)
        if q_filter:
            allowed_ids = Efiling.objects.filter(q_filter, id__in=efiling_ids).values_list("id", flat=True)
            if len(allowed_ids) != len(efiling_ids):
                raise ValidationError("You do not have permission to assign dates to some of these cases.")

        # Update all matching decisions. Note: in some cases (Division Bench) multiple judges 
        # have decisions for the same filing/date. We update all of them with the final date.
        updated = CourtroomJudgeDecision.objects.filter(
            efiling_id__in=efiling_ids, forwarded_for_date=fwd_date
        ).update(listing_date=ldate, reader_listing_remark=lremark)

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
            
        efiling.bench = None
        efiling.save(update_fields=["bench"])
        
        return Response({"detail": "Bench reset successful. Case returned to Scrutiny pool."}, status=drf_status.HTTP_200_OK)
