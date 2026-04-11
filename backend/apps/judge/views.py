from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Set
import logging

from django.contrib.auth.models import Group, AnonymousUser
from django.db import transaction
from django.db.models import Prefetch, Q

from django.urls import reverse
from django.utils import timezone
from rest_framework import status as drf_status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from apps.accounts.models import User
from apps.core.bench_config import (
    JUDGE_GROUP_TO_BENCH_TOKEN,
    get_bench_configurations,
    get_bench_configuration_for_stored_value,
    get_required_judge_groups,
)
from apps.core.models import Efiling, EfilingCaseDetails, EfilingDocumentsIndex, EfilingLitigant, EfilerDocumentAccess
from apps.efiling.party_display import build_petitioner_vs_respondent
from apps.efiling.serializers.efiling_document_index import EfilingDocumentsIndexSerializer

from .models import (
    CourtroomDecisionRequestedDocument,
    CourtroomDocumentAnnotation,
    CourtroomJudgeDecision,
    CourtroomSharedView,
    JUDGE_GROUP_CJ,
    JUDGE_GROUP_J1,
    JUDGE_GROUP_J2,
    JudgeDraftAnnotation,
)
from apps.reader.models import CourtroomForward, CourtroomForwardDocument, StenoOrderWorkflow
from apps.reader.workflow_state import apply_judge_decision
from apps.listing.models import CauseList, CauseListEntry
from .serializers import (
    CourtroomCaseDocumentAnnotationUpsertSerializer,
    CourtroomDecisionSerializer,
    CourtroomDocumentAnnotationSerializer,
    CourtroomPendingCaseSerializer,
    JudgeDraftAnnotationUpsertSerializer,
    JudgeStenoAnnotationsSnapshotSerializer,
    JudgeWorkflowDecisionSerializer,
)
from .bench_role import resolve_bench_role_group_for_forward

logger = logging.getLogger(__name__)


def _steno_draft_stream_url(request, document_index_id: int | None) -> str | None:
    if not document_index_id:
        return None
    path = reverse(
        "efiling:efiling-document-index-stream",
        kwargs={"document_index_id": int(document_index_id)},
    )
    return request.build_absolute_uri(path)

_DUMMY_TOKEN_TO_DUMMY_EMAIL: Dict[str, str] = {
    "judge_cj_dummy_token": "dummy_judge_cj@hcs.local",
    "judge_j1_dummy_token": "dummy_judge_j1@hcs.local",
    "judge_j2_dummy_token": "dummy_judge_j2@hcs.local",
    "advocate_dummy_token": "dummy_advocate@hcs.local",
}

_COURTROOM_JUDGE_GROUP_NAMES = frozenset(
    {
        "API_JUDGE",
        JUDGE_GROUP_CJ,
        JUDGE_GROUP_J1,
        JUDGE_GROUP_J2,
        *JUDGE_GROUP_TO_BENCH_TOKEN.keys(),
    }
)


def _auth_header_token(request) -> Optional[str]:
    auth = request.META.get("HTTP_AUTHORIZATION") or ""
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def _resolve_courtroom_user(request) -> User:
    """
    Resolve a Django User for courtroom endpoints (Judge or Advocate).
    """
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return user

    token = _auth_header_token(request)
    if not token:
        raise ValidationError({"detail": "Authentication required."})

    email = _DUMMY_TOKEN_TO_DUMMY_EMAIL.get(token)
    if not email:
        raise ValidationError({"detail": "Authentication required."})

    UserModel = get_user_model()
    try:
        return UserModel.objects.get(email=email)
    except UserModel.DoesNotExist as e:
        raise ValidationError({"detail": "User not provisioned."}) from e


def _resolve_judge_user(request) -> User:
    # Deprecated/Internal: uses unified resolver now
    return _resolve_courtroom_user(request)


def _user_judge_groups(user: User) -> Set[str]:
    if not user:
        return set()
    return set(user.groups.filter(name__in=_COURTROOM_JUDGE_GROUP_NAMES).values_list("name", flat=True))


def _assert_judge(request) -> User:
    user = _resolve_judge_user(request)
    if not _user_judge_groups(user):
        raise ValidationError({"detail": "Not authorized as judge."})
    return user


def _bench_required_groups(bench_key: str) -> Sequence[str]:
    req = get_required_judge_groups(bench_key)
    if not req:
        raise ValidationError({"bench_key": f"Unknown bench_key={bench_key}."})
    return req


def _judge_can_view_forward(
    user_groups: Set[str],
    bench_key: str,
    user: User | None = None,
) -> bool:
    if not user_groups or not bench_key:
        return False
    allowed = set(_allowed_bench_keys_for_judge(user_groups, user=user))
    return bench_key in allowed


def _assert_courtroom_user(request) -> User:
    return _resolve_courtroom_user(request)


def _validate_courtroom_access(
    user: User,
    efiling_id: int,
    date_obj_or_str: Any,
    *,
    allow_judge_unpublished: bool = False,
) -> Dict[str, Any]:
    """
    Enforce Publication-based access control.
    Returns metadata about the user role if access permitted.
    """
    is_judge = bool(_user_judge_groups(user))
    
    # 1. Resolve Date
    from datetime import date
    if isinstance(date_obj_or_str, str):
        cld = timezone.datetime.fromisoformat(date_obj_or_str).date()
    else:
        cld = date_obj_or_str

    # 2. Publication Check (Strict for advocates only)
    # Judges are allowed as long as the Reader forwarded it
    is_published = CauseListEntry.objects.filter(
        efiling_id=efiling_id,
        included=True,
        cause_list__cause_list_date=cld,
        cause_list__status=CauseList.CauseListStatus.PUBLISHED,
    ).exists()

    if is_judge:
        # Resolve user bench access
        user_groups = _user_judge_groups(user)
        forwards = CourtroomForward.objects.filter(efiling_id=efiling_id, forwarded_for_date=cld)
        has_bench_access = False
        for f in forwards:
            if _judge_can_view_forward(user_groups, f.bench_key, user=user) and _judge_sees_forward(
                user, f
            ):
                has_bench_access = True
                break
        
        if not has_bench_access:
            raise ValidationError({"detail": "Not authorized to view this case for your assigned bench."})

        # Enforce publish gate for judges unless explicitly bypassed
        # for pre-publish summary review flow.
        if (not allow_judge_unpublished) and (not is_published):
            raise ValidationError({"detail": "Case is not yet published in the cause list for this date."})

        return {"role": "JUDGE", "is_judge": True}
    else:
        # Advocate strict access control
        if not is_published:
             raise ValidationError({"detail": "Case is not yet published in the cause list for this date."})
        
        # [A] Direct association (EfilerDocumentAccess - Vakalatnama)
        has_access = EfilerDocumentAccess.objects.filter(e_filing_id=efiling_id, efiler=user).exists()
        
        # [B] Creator association (Fallback for e-filers)
        if not has_access:
            has_access = Efiling.objects.filter(id=efiling_id, created_by=user).exists()
            
        # [C] Dummy/Prototype Bypass (Dev only)
        if not has_access and user.email == "dummy_advocate@hcs.local":
            has_access = True

        if not has_access:
            raise ValidationError({"detail": f"You ({user.email}) are not authorized as an advocate for case #{efiling_id}."})
            
        return {"role": "ADVOCATE", "is_judge": False}


def _allowed_bench_keys_for_judge(user_groups: Set[str], user: User | None = None) -> list[str]:
    allowed_bench_keys: list[str] = []
    for bench in get_bench_configurations():
        if set(bench.judge_groups) & user_groups:
            allowed_bench_keys.append(bench.bench_key)
        if user is not None and bench.judge_user_ids and user.id in bench.judge_user_ids:
            allowed_bench_keys.append(bench.bench_key)
    for token_group, legacy_key in JUDGE_GROUP_TO_BENCH_TOKEN.items():
        if token_group in user_groups:
            allowed_bench_keys.append(legacy_key)
    if not allowed_bench_keys and user_groups & {
        JUDGE_GROUP_CJ,
        JUDGE_GROUP_J1,
        JUDGE_GROUP_J2,
        "API_JUDGE",
    }:
        if user is not None:
            for bench in get_bench_configurations():
                if bench.judge_user_ids and user.id in bench.judge_user_ids:
                    allowed_bench_keys.append(bench.bench_key)
        if not allowed_bench_keys:
            for bench in get_bench_configurations():
                if len(bench.judge_groups) == 1:
                    allowed_bench_keys.append(bench.bench_key)
    keys: Set[str] = set(allowed_bench_keys)
    for bk in list(keys):
        if "+" in bk:
            for part in bk.split("+"):
                p = part.strip()
                if p:
                    keys.add(p)
    return sorted(keys)


def _judge_should_see_forward_slot(user: User, forward: CourtroomForward) -> bool:
    """Division: each judge only sees the row for their slot (reader_slot_group)."""
    req = tuple(get_required_judge_groups(forward.bench_key))
    slot = (getattr(forward, "reader_slot_group", None) or "").strip()
    if not req:
        return False
    try:
        role = resolve_bench_role_group_for_forward(user, forward.bench_key)
    except ValueError:
        return False
    if slot:
        return slot == role
    if len(req) <= 1:
        return True
    return False


def _judge_sees_forward(user: User, forward: CourtroomForward) -> bool:
    return _judge_should_see_forward_slot(user, forward)


def _pick_courtroom_forward_from_candidates(
    user: User,
    candidates: list[CourtroomForward],
) -> CourtroomForward | None:
    """First matching forward for judge (bench + slot); advocates use first candidate."""
    if not candidates:
        return None
    if not _user_judge_groups(user):
        return candidates[0]
    user_groups = _user_judge_groups(user)
    allowed = set(_allowed_bench_keys_for_judge(user_groups, user=user))
    for f in candidates:
        if f.bench_key not in allowed:
            continue
        if not _judge_sees_forward(user, f):
            continue
        return f
    return None


def _resolve_courtroom_forward_for_case_view(
    user: User,
    efiling_id: int,
    *,
    forwarded_for_date: str | None,
    forward_bench_key: str | None,
    reader_slot_group: str | None,
) -> CourtroomForward | None:
    slot_q = (reader_slot_group or "").strip() or None
    bench_q = (forward_bench_key or "").strip() or None

    def base_qs(for_date: bool) -> Any:
        qs = CourtroomForward.objects.filter(efiling_id=efiling_id)
        if for_date and forwarded_for_date:
            qs = qs.filter(
                forwarded_for_date=timezone.datetime.fromisoformat(forwarded_for_date).date()
            )
        if bench_q:
            qs = qs.filter(bench_key=bench_q)
        if slot_q:
            qs = qs.filter(reader_slot_group=slot_q)
        return qs.order_by("-forwarded_for_date", "-id")

    forward = None
    if forwarded_for_date:
        forward = _pick_courtroom_forward_from_candidates(
            user, list(base_qs(for_date=True))
        )
    if not forward:
        forward = _pick_courtroom_forward_from_candidates(
            user, list(base_qs(for_date=False))
        )
    return forward


def _get_display_bench_for_efiling(
    efiling: Efiling | None,
    fallback_bench_key: str,
) -> tuple[str, str]:
    bench_config = get_bench_configuration_for_stored_value(
        getattr(efiling, "bench", None),
    )
    if bench_config:
        return bench_config.bench_key, bench_config.label
    return fallback_bench_key, fallback_bench_key


class CourtroomPendingCasesView(APIView):
    """
    Pending courtroom cases for a hearing date (`forwarded_for_date`).

    Judges: can see forwarded summaries pre-publish in dashboard buckets.
    (Case open/detail access is separately publish-gated.)

    Advocates: only published, included entries on the cause list for that date, and only
    cases they are allowed to represent.
    """

    def get(self, request, *args, **kwargs):
        user = _resolve_courtroom_user(request)
        user_groups = _user_judge_groups(user)
        is_judge = bool(user_groups)

        forwarded_for_date = request.query_params.get("forwarded_for_date")
        if forwarded_for_date:
            forwarded_date = timezone.datetime.fromisoformat(forwarded_for_date).date()
        else:
            forwarded_date = timezone.now().date()

        # Published cause list entries for this date (advocate visibility + judge bucketing)
        listed_efiling_ids = set(
            CauseListEntry.objects.filter(
                cause_list__cause_list_date=forwarded_date,
                cause_list__status=CauseList.CauseListStatus.PUBLISHED,
                included=True,
            ).values_list("efiling_id", flat=True)
        )

        # Advocates have nothing to see until something is on a published list for that date.
        if not is_judge and not listed_efiling_ids:
            return Response({"pending_for_listing": [], "pending_for_causelist": []}, status=drf_status.HTTP_200_OK)

        base_forwards = CourtroomForward.objects.filter(forwarded_for_date=forwarded_date)

        if is_judge:
            forwards = (
                base_forwards.select_related("efiling")
                .prefetch_related("efiling__litigants")
                .order_by("-id")
            )
        else:
            forwards = (
                base_forwards.filter(efiling_id__in=listed_efiling_ids)
                .select_related("efiling")
                .prefetch_related("efiling__litigants")
                .order_by("-id")
            )

        if is_judge:
            allowed_bench_keys = set(_allowed_bench_keys_for_judge(user_groups, user=user))
        else:
            accessible_ids = set(EfilerDocumentAccess.objects.filter(efiler=user).values_list("e_filing_id", flat=True))
            creator_ids = set(Efiling.objects.filter(created_by=user).values_list("id", flat=True))
            accessible_ids.update(creator_ids)
            if user.email == "dummy_advocate@hcs.local":
                accessible_ids.update(listed_efiling_ids)

        def build_item(f: CourtroomForward) -> dict:
            display_bench_key, display_bench_label = _get_display_bench_for_efiling(
                f.efiling, f.bench_key
            )
            decision = None
            if is_judge:
                decision = (
                    CourtroomJudgeDecision.objects.filter(
                        judge_user=user,
                        efiling_id=f.efiling_id,
                        forwarded_for_date=f.forwarded_for_date,
                    )
                    .only("approved", "listing_date", "status")
                    .first()
                )

            item = {
                "efiling_id": f.efiling_id,
                "e_filing_number": getattr(f.efiling, "e_filing_number", None),
                "case_number": f.efiling.case_number,
                "bench_key": display_bench_key,
                "bench_label": display_bench_label,
                "forward_bench_key": f.bench_key,
                "reader_slot_group": getattr(f, "reader_slot_group", None) or "",
                "petitioner_name": getattr(f.efiling, "petitioner_name", None),
                "petitioner_vs_respondent": getattr(
                    f.efiling, "petitioner_vs_respondent_display", "-"
                ),
                "filing_date": (
                    getattr(f.efiling, "filing_date", None).isoformat()
                    if getattr(f.efiling, "filing_date", None)
                    else None
                ),
                "listing_summary": f.listing_summary,
                "forwarded_for_date": f.forwarded_for_date.isoformat(),
                "judge_decision": (decision.approved if decision else None),
                "judge_decision_status": (decision.status if decision else None),
                "judge_listing_date": (
                    str(decision.listing_date) if decision and decision.listing_date else None
                ),
            }

            if is_judge and decision:
                req_docs = list(
                    decision.requested_documents.select_related("efiling_document_index").values(
                        "efiling_document_index_id",
                        "efiling_document_index__document_part_name",
                        "efiling_document_index__document__document_type",
                    )
                )
                item["requested_document_count"] = len(req_docs)
                item["requested_documents"] = [
                    {
                        "document_index_id": r["efiling_document_index_id"],
                        "document_part_name": r.get("efiling_document_index__document_part_name"),
                        "document_type": r.get("efiling_document_index__document__document_type"),
                    }
                    for r in req_docs
                ]
            else:
                item["requested_document_count"] = 0
                item["requested_documents"] = []

            return item

        pending_for_listing: List[dict] = []
        pending_for_causelist: List[dict] = []
        seen_pre: Set[tuple[int, str, str]] = set()
        seen_pub: Set[tuple[int, str, str]] = set()

        def _row_key(f: CourtroomForward) -> tuple[int, str, str]:
            return (f.efiling_id, f.bench_key, getattr(f, "reader_slot_group", None) or "")

        for f in forwards:
            if is_judge:
                if f.bench_key not in allowed_bench_keys:
                    continue
                if not _judge_sees_forward(user, f):
                    continue
            else:
                if f.efiling_id not in accessible_ids:
                    continue

            on_published_list = f.efiling_id in listed_efiling_ids
            rk = _row_key(f)

            if is_judge:
                if on_published_list:
                    if rk in seen_pub:
                        continue
                    seen_pub.add(rk)
                    pending_for_causelist.append(build_item(f))
                else:
                    if rk in seen_pre:
                        continue
                    seen_pre.add(rk)
                    pending_for_listing.append(build_item(f))
            else:
                if rk in seen_pub:
                    continue
                seen_pub.add(rk)
                pending_for_causelist.append(build_item(f))

        return Response(
            {
                "pending_for_listing": pending_for_listing,
                "pending_for_causelist": pending_for_causelist,
            },
            status=drf_status.HTTP_200_OK,
        )



class CourtroomCaseDocumentsView(APIView):
    """
    Unified: get document index items for the case.
    Judges: see annotations.
    Advocates: see only documents.
    """

    def get(self, request, efiling_id: int, *args, **kwargs):
        user = _resolve_courtroom_user(request)
        forwarded_for_date = request.query_params.get("forwarded_for_date")
        forward_bench_key = str(request.query_params.get("forward_bench_key") or "").strip() or None
        reader_slot_group = str(request.query_params.get("reader_slot_group") or "").strip() or None

        # 1. Permission and Publication Check
        access_meta = _validate_courtroom_access(
            user,
            efiling_id,
            forwarded_for_date,
            allow_judge_unpublished=True,
        )
        is_judge = access_meta.get("is_judge", False)

        # 2. Forward row (division: disambiguate with reader_slot_group)
        forward = _resolve_courtroom_forward_for_case_view(
            user,
            efiling_id,
            forwarded_for_date=forwarded_for_date,
            forward_bench_key=forward_bench_key,
            reader_slot_group=reader_slot_group or None,
        )

        if not forward:
            raise ValidationError({"detail": "Case forward record not found."})

        requested_only = str(request.query_params.get("requested_only", "")).strip().lower() in {"1", "true", "yes", "y"}

        doc_indexes_qs = EfilingDocumentsIndex.objects.filter(
            document__e_filing_id=efiling_id, is_active=True
        ).select_related("document", "document__e_filing").order_by("id")
        
        # SYNC MODIFICATION: Only show documents specifically selected for the hearing (Hearing Pack)
        selected_ids = list(forward.selected_documents.values_list("efiling_document_index_id", flat=True))
        if selected_ids:
            doc_indexes_qs = doc_indexes_qs.filter(id__in=selected_ids)

        if requested_only and is_judge:
            decision = (
                CourtroomJudgeDecision.objects.filter(
                    judge_user=user,
                    efiling_id=efiling_id,
                    forwarded_for_date=forward.forwarded_for_date,
                )
                .order_by("-id")
                .first()
            )
            requested_ids = (
                list(decision.requested_documents.values_list("efiling_document_index_id", flat=True))
                if decision else []
            )
            if requested_ids:
                doc_indexes_qs = doc_indexes_qs.filter(id__in=requested_ids)

        serializer = EfilingDocumentsIndexSerializer(doc_indexes_qs, many=True, context={"request": request})
        doc_items = serializer.data

        # 3. Judge Annotations (Judge-only)
        if is_judge:
            existing = CourtroomDocumentAnnotation.objects.filter(
                judge_user=user, efiling_document_index__in=doc_indexes_qs
            )
            anno_map = {a.efiling_document_index_id: a for a in existing}
            for item in doc_items:
                idx_id = item.get("id")
                anno = anno_map.get(idx_id)
                item["annotation_text"] = anno.annotation_text if anno else (item.get("draft_comments") or item.get("comments") or None)
                item["annotation_data"] = anno.annotation_data if anno else {}
        else:
            # Strip internal comments for advocates
            for item in doc_items:
                item["annotation_text"] = None
                item["annotation_data"] = {}
                item["draft_comments"] = None
                item["comments"] = None

        return Response({"items": doc_items}, status=drf_status.HTTP_200_OK)


class CourtroomCaseSummaryView(APIView):
    """
    Unified: get case summary details.
    """

    def get(self, request, efiling_id: int, *args, **kwargs):
        user = _resolve_courtroom_user(request)
        forwarded_for_date = request.query_params.get("forwarded_for_date")
        forward_bench_key = str(request.query_params.get("forward_bench_key") or "").strip() or None
        reader_slot_group = str(request.query_params.get("reader_slot_group") or "").strip() or None

        # 1. Permission and Publication Check
        access_meta = _validate_courtroom_access(
            user,
            efiling_id,
            forwarded_for_date,
            allow_judge_unpublished=True,
        )
        is_judge = access_meta.get("is_judge", False)

        forward = _resolve_courtroom_forward_for_case_view(
            user,
            efiling_id,
            forwarded_for_date=forwarded_for_date,
            forward_bench_key=forward_bench_key,
            reader_slot_group=reader_slot_group or None,
        )
        if not forward:
            raise ValidationError({"detail": "Case not forwarded for this user/date."})

        filing = Efiling.objects.filter(id=efiling_id).prefetch_related("litigants").first()
        if not filing:
            raise ValidationError({"detail": "Case not found."})

        display_bench_key, display_bench_label = _get_display_bench_for_efiling(filing, forward.bench_key)

        litigants = list(
            EfilingLitigant.objects.filter(e_filing_id=efiling_id)
            .only("name", "is_petitioner", "sequence_number")
            .order_by("is_petitioner", "sequence_number", "id")
            .values("id", "name", "is_petitioner", "sequence_number")
        )
        selected_documents = list(
            forward.selected_documents.select_related("efiling_document_index")
            .values(
                "efiling_document_index_id",
                "efiling_document_index__document_part_name",
                "efiling_document_index__document__document_type",
                "efiling_document_index__file_part_path",
            )
        )
        
        case_detail = (
            EfilingCaseDetails.objects.filter(e_filing_id=efiling_id)
            .select_related("dispute_state", "dispute_district")
            .order_by("-id")
            .first()
        )

        # 3. Decision metadata (Judge-only)
        latest_decision_data = None
        if is_judge:
            latest_decision = CourtroomJudgeDecision.objects.filter(
                judge_user=user,
                efiling_id=efiling_id,
                forwarded_for_date=forward.forwarded_for_date,
            ).order_by("-id").first()
            if latest_decision:
                latest_decision_data = {
                    "status": latest_decision.status,
                    "approved": latest_decision.approved,
                    "decision_notes": latest_decision.decision_notes,
                }

        return Response(
            {
                "efiling_id": filing.id,
                "case_number": filing.case_number,
                "e_filing_number": filing.e_filing_number,
                "petitioner_name": filing.petitioner_name,
                "petitioner_vs_respondent": filing.petitioner_vs_respondent_display,
                "filing_date": filing.filing_date.isoformat() if getattr(filing, "filing_date", None) else None,
                "petitioner_contact": filing.petitioner_contact,
                "bench_key": display_bench_key,
                "bench_label": display_bench_label,
                "forward_bench_key": forward.bench_key,
                "reader_slot_group": getattr(forward, "reader_slot_group", None) or "",
                "forwarded_for_date": forward.forwarded_for_date.isoformat(),
                "listing_summary": forward.listing_summary,
                "is_published": True, # By reaching here, we know it's published
                "selected_documents": [
                    {
                        "document_index_id": d["efiling_document_index_id"],
                        "document_part_name": d.get("efiling_document_index__document_part_name"),
                        "document_type": d.get("efiling_document_index__document__document_type"),
                        "file_url": d.get("efiling_document_index__file_part_path"),
                    }
                    for d in selected_documents
                ],
                "judge_decision": latest_decision_data,
                "litigants": litigants,
                "case_details": (
                    {
                        "cause_of_action": getattr(case_detail, "cause_of_action", None),
                        "date_of_cause_of_action": (
                            case_detail.date_of_cause_of_action.isoformat()
                            if getattr(case_detail, "date_of_cause_of_action", None)
                            else None
                        ),
                        "dispute_state": (
                            case_detail.dispute_state.state
                            if getattr(case_detail, "dispute_state", None)
                            else None
                        ),
                        "dispute_district": (
                            case_detail.dispute_district.district
                            if getattr(case_detail, "dispute_district", None)
                            else None
                        ),
                        "dispute_taluka": getattr(case_detail, "dispute_taluka", None),
                    }
                    if case_detail
                    else None
                ),
            },
            status=drf_status.HTTP_200_OK,
        )


class CourtroomDocumentAnnotationView(APIView):
    """
    Judge: upsert annotation text for a document index.
    """

    def post(self, request, *args, **kwargs):
        user = _assert_judge(request)
        payload = CourtroomCaseDocumentAnnotationUpsertSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        doc_index_id = payload.validated_data["efiling_document_index_id"]
        annotation_text = payload.validated_data.get("annotation_text")
        annotation_data = payload.validated_data.get("annotation_data") or {}

        # Authorization: only allow annotating documents belonging to efilings
        # that were forwarded for a bench where this judge role applies.
        doc_index = (
            EfilingDocumentsIndex.objects.select_related("document")
            .filter(id=doc_index_id)
            .first()
        )
        if not doc_index or not doc_index.document_id:
            raise ValidationError({"efiling_document_index_id": "Invalid document index."})

        user_groups = _user_judge_groups(user)
        allowed_bench_keys = set(_allowed_bench_keys_for_judge(user_groups, user=user))
        if not any(
            f.bench_key in allowed_bench_keys and _judge_sees_forward(user, f)
            for f in CourtroomForward.objects.filter(efiling_id=doc_index.document.e_filing_id)
        ):
            raise ValidationError({"detail": "Not authorized to annotate this document."})

        ann, _ = CourtroomDocumentAnnotation.objects.update_or_create(
            judge_user=user,
            efiling_document_index_id=doc_index_id,
            defaults={
                "annotation_text": annotation_text,
                "annotation_data": annotation_data,
            },
        )
        return Response(
            {
                "efiling_document_index": doc_index_id,
                "annotation_text": ann.annotation_text,
                "annotation_data": ann.annotation_data,
            },
            status=drf_status.HTTP_200_OK,
        )


class CourtroomDecisionView(APIView):
    """
    Judge: save a decision for a forwarded case and return it to reader flow.
    """

    def post(self, request, *args, **kwargs):
        user = _assert_judge(request)
        payload = CourtroomDecisionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        efiling_id = payload.validated_data["efiling_id"]
        forwarded_for_date = payload.validated_data["forwarded_for_date"]
        forward_bench_key = payload.validated_data.get("forward_bench_key")
        reader_slot_group = (payload.validated_data.get("reader_slot_group") or "").strip() or None
        status = CourtroomJudgeDecision.DecisionStatus.APPROVED
        requested_document_index_ids = payload.validated_data.get("requested_document_index_ids") or []
        approved = True
        decision_notes = payload.validated_data.get("decision_notes")
        user_groups = _user_judge_groups(user)
        # Ensure there is an authorized forward row and resolve an unambiguous
        # bench role slot for this decision.
        fwd_qs = CourtroomForward.objects.filter(
            efiling_id=efiling_id,
            forwarded_for_date=forwarded_for_date,
        )
        if forward_bench_key:
            fwd_qs = fwd_qs.filter(bench_key=forward_bench_key)
        if reader_slot_group:
            fwd_qs = fwd_qs.filter(reader_slot_group=reader_slot_group)
        candidate_forwards = list(fwd_qs.order_by("-id"))
        if not candidate_forwards:
            raise ValidationError({"detail": "Case not forwarded for this date."})
        resolved_candidates: list[tuple[CourtroomForward, str]] = []
        for fwd in candidate_forwards:
            if not _judge_can_view_forward(user_groups, fwd.bench_key, user=user):
                continue
            if not _judge_sees_forward(user, fwd):
                continue
            try:
                role_group = resolve_bench_role_group_for_forward(user, fwd.bench_key)
            except ValueError:
                continue
            resolved_candidates.append((fwd, role_group))

        if not resolved_candidates:
            raise ValidationError(
                {
                    "detail": (
                        "Unable to resolve judge role slot for this bench. "
                        "Configure judge role mapping (CJ/J1/J2)."
                    )
                }
            )
        if forward_bench_key:
            resolved_candidates = [
                item for item in resolved_candidates if item[0].bench_key == forward_bench_key
            ]
            if not resolved_candidates:
                raise ValidationError({"detail": "Not authorized for the selected bench slot."})
        distinct_roles = {role for _, role in resolved_candidates}
        if len(distinct_roles) > 1:
            # Prefer exact bench-slot forwards (single required group) to avoid cross-slot collisions
            # when users are API_JUDGE-like in legacy deployments.
            scoped = []
            for fwd, role in resolved_candidates:
                req = tuple(get_required_judge_groups(fwd.bench_key))
                if len(req) == 1:
                    scoped.append((fwd, req[0]))
            if scoped:
                resolved_candidates = scoped
                distinct_roles = {role for _, role in resolved_candidates}
        if len(distinct_roles) > 1:
            raise ValidationError(
                {
                    "detail": (
                        "Ambiguous judge role for this case/date. "
                        "Open the case from the specific bench slot and submit again."
                    )
                }
            )
        _forward, bench_role_group = resolved_candidates[0]

        conflict_exists = CourtroomJudgeDecision.objects.filter(
            efiling_id=efiling_id,
            forwarded_for_date=forwarded_for_date,
            bench_role_group=bench_role_group,
        ).exclude(judge_user_id=user.id).exists()
        if conflict_exists:
            raise ValidationError(
                {
                    "detail": (
                        "This bench role slot is already recorded by another judge "
                        "for the selected case/date."
                    )
                }
            )

        obj, _created = CourtroomJudgeDecision.objects.update_or_create(
            judge_user=user,
            efiling_id=efiling_id,
            forwarded_for_date=forwarded_for_date,
            defaults={
                "status": status,
                "approved": approved,
                "decision_notes": decision_notes,
                "bench_role_group": bench_role_group,
            },
        )
        try:
            apply_judge_decision(
                efiling_id=int(efiling_id),
                forwarded_for_date=forwarded_for_date,
                bench_key=str(_forward.bench_key),
                bench_role_group=str(bench_role_group),
                judge_user_id=int(user.id),
                status=str(status),
                approved=bool(approved),
                decision_notes=decision_notes,
            )
        except Exception:
            logger.exception("bench workflow state judge-decision dual-write failed")
        valid_req_doc_ids = set()
        if requested_document_index_ids:
            valid_req_doc_ids = set(
                EfilingDocumentsIndex.objects.filter(
                    id__in=requested_document_index_ids,
                    document__e_filing_id=efiling_id,
                ).values_list("id", flat=True)
            )
        CourtroomDecisionRequestedDocument.objects.filter(judge_decision=obj).exclude(
            efiling_document_index_id__in=valid_req_doc_ids
        ).delete()
        for doc_id in valid_req_doc_ids:
            CourtroomDecisionRequestedDocument.objects.get_or_create(
                judge_decision=obj,
                efiling_document_index_id=doc_id,
            )

        return Response(
            {
                "efiling_id": efiling_id,
                "status": obj.status,
                "approved": obj.approved,
                "requested_document_count": len(valid_req_doc_ids),
            },
            status=drf_status.HTTP_200_OK,
        )


class CourtroomApprovedLookupView(APIView):
    """
    Listing Officer: bulk lookup which efilings are judge-approved for a given bench_key and cause_list_date.
    GET is used with query params as per plan.
    """

    def get(self, request, *args, **kwargs):
        cause_list_date = request.query_params.get("cause_list_date")
        bench_key = request.query_params.get("bench_key")
        if not cause_list_date or not bench_key:
            raise ValidationError({"cause_list_date": "Required.", "bench_key": "Required."})

        cld = timezone.datetime.fromisoformat(cause_list_date).date()
        required_groups = _bench_required_groups(bench_key)

        forwarded_ids = set(
            CourtroomForward.objects.filter(
                bench_key=bench_key,
                forwarded_for_date=cld,
            ).values_list("efiling_id", flat=True)
        )
        if not forwarded_ids:
            return Response({"efiling_ids": []}, status=drf_status.HTTP_200_OK)

        # Strict rule: each required group must have at least one approving judge
        # for the same forwarded_for_date and same listing_date.
        group_to_ids: List[Set[int]] = []
        for group_name in required_groups:
            ids = set(
                CourtroomJudgeDecision.objects.filter(
                    judge_user__groups__name=group_name,
                    efiling_id__in=forwarded_ids,
                    forwarded_for_date=cld,
                    listing_date=cld,
                    approved=True,
                ).values_list("efiling_id", flat=True)
            )
            group_to_ids.append(ids)

        eligible_ids: Set[int] = set.intersection(*group_to_ids) if group_to_ids else set()

        return Response({"efiling_ids": sorted(list(eligible_ids))}, status=drf_status.HTTP_200_OK)


class CourtroomDecisionCalendarView(APIView):
    """
    Judge: list all of my decisions for calendar rendering.
    """

    def get(self, request, *args, **kwargs):
        user = _assert_judge(request)
        rows = (
            CourtroomJudgeDecision.objects.filter(judge_user=user)
            .select_related("efiling")
            .prefetch_related("efiling__litigants")
            .order_by("-listing_date", "-forwarded_for_date", "-id")
        )
        items = []
        for row in rows:
            ef = row.efiling
            items.append(
                {
                    "efiling_id": row.efiling_id,
                    "e_filing_number": getattr(ef, "e_filing_number", None),
                    "case_number": row.efiling.case_number,
                    "petitioner_name": getattr(ef, "petitioner_name", None),
                    "petitioner_vs_respondent": getattr(ef, "petitioner_vs_respondent_display", "-"),
                    "filing_date": getattr(ef, "filing_date", None).isoformat() if getattr(ef, "filing_date", None) else None,
                    "status": row.status,
                    "approved": row.approved,
                    "listing_date": row.listing_date.isoformat()
                    if row.listing_date
                    else None,
                    "forwarded_for_date": row.forwarded_for_date.isoformat()
                    if row.forwarded_for_date
                    else None,
                    "decision_notes": row.decision_notes,
                }
            )
        return Response({"items": items}, status=drf_status.HTTP_200_OK)





class CourtroomSharedViewAPIView(APIView):
    """
    Real-time document sharing between Advocate and Judge.
    - Advocate POSTs to update position.
    - Judge GETs to poll for active share.
    - Advocate DELETEs to stop sharing.
    """

    def get(self, request, *args, **kwargs):
        # Called by Judge to poll for active advocate share
        efiling_id = request.query_params.get("efiling_id")
        if not efiling_id:
             raise ValidationError({"efiling_id": "Required."})
        
        # Get latest active share for this case
        share = (
            CourtroomSharedView.objects.filter(efiling_id=efiling_id, is_active=True)
            .select_related("advocate_user")
            .order_by("-updated_at")
            .first()
        )

        if not share:
            return Response({"active": False}, status=drf_status.HTTP_200_OK)
        
        return Response({
            "active": True,
            "document_index_id": share.document_index_id,
            "page_index": share.page_index,
            "advocate_name": share.advocate_user.get_full_name() or share.advocate_user.email
        }, status=drf_status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Called by Advocate to update position or start sharing
        # Use existing judge resolver logic pattern but for advocate
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            # Fallback for dev/dummy environments if standard auth isn't active
            token = _auth_header_token(request)
            if token == "advocate_dummy_token":
                from django.contrib.auth import get_user_model
                UserModel = get_user_model()
                user = UserModel.objects.filter(email="dummy_advocate@hcs.local").first()
        
        if not user or not user.is_authenticated:
            raise ValidationError({"detail": "advocate Authentication required."})

        efiling_id = request.data.get("efiling_id")
        doc_id = request.data.get("document_index_id")
        page_idx = request.data.get("page_index", 0)

        if not efiling_id or not doc_id:
             raise ValidationError({"efiling_id": "Required.", "document_index_id": "Required."})

        share, _ = CourtroomSharedView.objects.update_or_create(
            efiling_id=efiling_id,
            advocate_user=user,
            defaults={
                "document_index_id": doc_id,
                "page_index": page_idx,
                "is_active": True,
                "updated_at": timezone.now()
            }
        )
        return Response({"status": "success", "is_active": True}, status=drf_status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        # Called by Advocate to stop sharing
        efiling_id = request.query_params.get("efiling_id")
        user = getattr(request, "user", None)
        # If dummy token, resolve user
        if not user or not user.is_authenticated:
            token = _auth_header_token(request)
            if token == "advocate_dummy_token":
                from django.contrib.auth import get_user_model
                UserModel = get_user_model()
                user = UserModel.objects.filter(email="dummy_advocate@hcs.local").first()

        CourtroomSharedView.objects.filter(
            efiling_id=efiling_id, advocate_user=user
        ).update(is_active=False, updated_by=user, updated_at=timezone.now())
        
        return Response({"status": "inactive"}, status=drf_status.HTTP_200_OK)


class JudgeStenoWorkflowListView(APIView):
    def get(self, request, *args, **kwargs):
        _assert_judge(request)
        ann_qs = JudgeDraftAnnotation.objects.filter(is_active=True).order_by("id")
        rows = (
            StenoOrderWorkflow.objects.filter(
                workflow_status__in=[
                    StenoOrderWorkflow.WorkflowStatus.SENT_FOR_JUDGE_APPROVAL,
                    StenoOrderWorkflow.WorkflowStatus.CHANGES_REQUESTED,
                    StenoOrderWorkflow.WorkflowStatus.JUDGE_APPROVED,
                    StenoOrderWorkflow.WorkflowStatus.SIGNED_AND_PUBLISHED,
                ],
                is_active=True,
            )
            .select_related("efiling", "proceeding", "draft_document_index")
            .prefetch_related(Prefetch("judge_annotations", queryset=ann_qs))
            .order_by("-updated_at", "-id")
        )
        items = []
        for row in rows:
            draft_id = row.draft_document_index_id
            ann_list = [
                {
                    "id": a.id,
                    "note_text": a.note_text,
                    "page_number": a.page_number,
                    "status": a.status,
                    "annotation_type": a.annotation_type,
                    "x": str(a.x) if a.x is not None else None,
                    "y": str(a.y) if a.y is not None else None,
                    "width": str(a.width) if a.width is not None else None,
                    "height": str(a.height) if a.height is not None else None,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in row.judge_annotations.all()
            ]
            items.append(
                {
                    "workflow_id": row.id,
                    "efiling_id": row.efiling_id,
                    "case_number": row.efiling.case_number,
                    "e_filing_number": row.efiling.e_filing_number,
                    "document_type": row.document_type,
                    "draft_document_index_id": draft_id,
                    "draft_preview_url": _steno_draft_stream_url(request, draft_id),
                    "workflow_status": row.workflow_status,
                    "judge_approval_status": row.judge_approval_status,
                    "proceedings_text": row.proceeding.proceedings_text,
                    "reader_remark": row.proceeding.reader_remark,
                    "hearing_date": row.proceeding.hearing_date.isoformat(),
                    "next_listing_date": row.proceeding.next_listing_date.isoformat(),
                    "judge_annotations": ann_list,
                }
            )
        return Response({"items": items}, status=drf_status.HTTP_200_OK)


class JudgeStenoWorkflowAnnotationView(APIView):
    def post(self, request, *args, **kwargs):
        judge_user = _assert_judge(request)
        payload = JudgeDraftAnnotationUpsertSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        workflow = StenoOrderWorkflow.objects.filter(
            id=payload.validated_data["workflow_id"], is_active=True
        ).first()
        if not workflow:
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        annotation = JudgeDraftAnnotation.objects.create(
            workflow=workflow,
            page_number=payload.validated_data.get("page_number"),
            x=payload.validated_data.get("x"),
            y=payload.validated_data.get("y"),
            width=payload.validated_data.get("width"),
            height=payload.validated_data.get("height"),
            annotation_type=payload.validated_data.get("annotation_type"),
            note_text=payload.validated_data["note_text"],
            created_by=judge_user,
            updated_by=judge_user,
        )
        return Response(
            {"annotation_id": annotation.id, "status": annotation.status},
            status=drf_status.HTTP_200_OK,
        )


class JudgeStenoWorkflowAnnotationsSnapshotView(APIView):
    """
    Replace all *positional* mark-up for a workflow (canvas marks) in one request.
    Rows with no page and no x/y (quick text-only notes) are kept.
    """

    def post(self, request, *args, **kwargs):
        judge_user = _assert_judge(request)
        payload = JudgeStenoAnnotationsSnapshotSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        workflow = StenoOrderWorkflow.objects.filter(
            id=payload.validated_data["workflow_id"], is_active=True
        ).first()
        if not workflow:
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        positional = (
            Q(page_number__isnull=False)
            | Q(x__isnull=False)
            | Q(y__isnull=False)
            | Q(width__isnull=False)
            | Q(height__isnull=False)
        )
        rows = payload.validated_data["annotations"]
        with transaction.atomic():
            JudgeDraftAnnotation.objects.filter(workflow=workflow).filter(positional).delete()
            for row in rows:
                JudgeDraftAnnotation.objects.create(
                    workflow=workflow,
                    page_number=row.get("page_number"),
                    x=row.get("x"),
                    y=row.get("y"),
                    width=row.get("width"),
                    height=row.get("height"),
                    annotation_type=row.get("annotation_type"),
                    note_text=row["note_text"],
                    created_by=judge_user,
                    updated_by=judge_user,
                )
        return Response({"saved": len(rows)}, status=drf_status.HTTP_200_OK)


class JudgeStenoWorkflowDecisionView(APIView):
    def post(self, request, *args, **kwargs):
        judge_user = _assert_judge(request)
        payload = JudgeWorkflowDecisionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        workflow = StenoOrderWorkflow.objects.filter(
            id=payload.validated_data["workflow_id"], is_active=True
        ).first()
        if not workflow:
            raise ValidationError({"workflow_id": "Invalid workflow_id."})
        status = payload.validated_data["judge_approval_status"]
        notes = payload.validated_data.get("judge_approval_notes")
        if status == "APPROVED":
            workflow.judge_approval_status = StenoOrderWorkflow.JudgeApprovalStatus.APPROVED
            workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.JUDGE_APPROVED
            workflow.judge_approved_by = judge_user
            workflow.judge_approved_at = timezone.now()
        else:
            workflow.judge_approval_status = StenoOrderWorkflow.JudgeApprovalStatus.REJECTED
            workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.CHANGES_REQUESTED
        workflow.judge_approval_notes = notes
        workflow.updated_by = judge_user
        workflow.save(
            update_fields=[
                "judge_approval_status",
                "workflow_status",
                "judge_approved_by",
                "judge_approved_at",
                "judge_approval_notes",
                "updated_by",
                "updated_at",
            ]
        )
        return Response(
            {
                "workflow_status": workflow.workflow_status,
                "judge_approval_status": workflow.judge_approval_status,
            },
            status=drf_status.HTTP_200_OK,
        )
