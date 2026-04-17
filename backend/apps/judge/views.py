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
    bench_key_aliases_for_seated_judge,
    get_bench_configuration_for_stored_value,
    get_required_judge_groups,
    judge_user_seated_on_bench_key,
)
from apps.core.models import (
    CivilT,
    Efiling,
    EfilingCaseDetails,
    EfilingDocumentsIndex,
    EfilingLitigant,
    EfilerDocumentAccess,
    JudgeT,
    ReaderJudgeAssignment,
)
from apps.cis.models import OrderDetailsA
from apps.efiling.party_display import build_petitioner_vs_respondent
from apps.efiling.serializers.efiling_document_index import EfilingDocumentsIndexSerializer

from .models import (
    CourtroomDecisionRequestedDocument,
    CourtroomDocumentAnnotation,
    CourtroomJudgeDecision,
    CourtroomSharedView,
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

_COURTROOM_JUDGE_GROUP_NAMES = frozenset({"JUDGE"})


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


def _judge_can_view_forward(user: User, bench_key: str) -> bool:
    if not bench_key or not _user_judge_groups(user):
        return False
    return judge_user_seated_on_bench_key(user, bench_key)


def _bench_key_aliases_list_for_judge(user: User) -> list[str]:
    return sorted(bench_key_aliases_for_seated_judge(user))


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
        # Any forward for this filing where the judge is seated on the bench — do not require
        # forwarded_for_date to match the URL date (reader may have merged rows on an older day
        # or the hearing calendar day may differ from CourtroomForward.forwarded_for_date).
        forwards_any = CourtroomForward.objects.filter(efiling_id=efiling_id)
        has_bench_access = any(
            _judge_can_view_forward(user, f.bench_key) for f in forwards_any
        )

        # Hearing day may follow published cause list while reader forward used another calendar day.
        if not has_bench_access and is_published:
            for ent in CauseListEntry.objects.filter(
                efiling_id=efiling_id,
                included=True,
                cause_list__cause_list_date=cld,
                cause_list__status=CauseList.CauseListStatus.PUBLISHED,
            ).select_related("cause_list"):
                if _judge_can_view_forward(user, str(ent.cause_list.bench_key)):
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


def _resolve_efiling_cino(efiling: Efiling) -> str | None:
    case_number = (getattr(efiling, "case_number", None) or "").strip()
    if case_number:
        row = CivilT.objects.filter(case_no=case_number).values("cino").first()
        cino = (row or {}).get("cino")
        if cino:
            return str(cino)
    fallback = (case_number or (getattr(efiling, "e_filing_number", None) or "")).strip()
    return fallback[:16] if fallback else None


def _order_upload_url(request, value: str | None) -> str | None:
    raw = (value or "").strip()
    if not raw:
        return None
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    if raw.startswith("/"):
        return request.build_absolute_uri(raw)
    return request.build_absolute_uri(f"/{raw}")


def _orders_for_efiling(request, efiling: Efiling) -> list[dict]:
    cino = _resolve_efiling_cino(efiling)
    if not cino:
        return []
    rows = (
        OrderDetailsA.objects.filter(cino=cino)
        .order_by("-timestamp", "-order_no")[:100]
    )
    items: list[dict] = []
    for row in rows:
        phase = (row.download or "").strip().upper()
        if phase == "DRAFT":
            label = "Draft"
        elif phase == "APPROVED_DRAFT":
            label = "Approved Draft"
        elif phase == "SIGNED_FINAL":
            label = "Final Signed"
        elif phase == "PUBLISHED":
            label = "Published"
        else:
            label = phase or "Order"
        items.append(
            {
                "order_no": row.order_no,
                "status": label,
                "uploaded_at": row.timestamp.isoformat() if row.timestamp else None,
                "file_url": _order_upload_url(request, row.upload),
            }
        )
    return items


def _courtroom_forward_matches_judge_slot(user: User, forward: CourtroomForward) -> bool:
    """
    Whether this forward row is the one this judge should see (per bench_role_group / legacy RJA).
    """
    if not _judge_can_view_forward(user, forward.bench_key):
        return False
    brg = (getattr(forward, "bench_role_group", None) or "").strip()
    required_groups = tuple(get_required_judge_groups(forward.bench_key))
    try:
        role = resolve_bench_role_group_for_forward(user, forward.bench_key)
    except ValueError:
        return False
    if brg:
        return brg == str(role)
    # Legacy rows may not carry bench_role_group. For single-seat benches,
    # bench access + resolved slot is sufficient and must not depend on summary text.
    if len(required_groups) <= 1:
        return True
    # Division-bench legacy fallback: map reader->judge seating through RJA.
    fwd_uid = getattr(getattr(forward, "forwarded_by", None), "id", None)
    if fwd_uid is None:
        return False
    judge_ids = list(JudgeT.objects.filter(user_id=user.id).values_list("id", flat=True))
    if not judge_ids:
        return False
    reader_ids = set(
        ReaderJudgeAssignment.objects.filter(judge_id__in=judge_ids).values_list(
            "reader_user_id", flat=True
        )
    )
    return int(fwd_uid) in reader_ids


def _listing_summary_visible_to_judge(user: User, forward: CourtroomForward) -> str | None:
    """
    Division benches: show summary only for this judge's slot row (bench_role_group) or legacy RJA match.
    Single-judge benches: show summary as before.
    """
    text = (getattr(forward, "listing_summary", None) or "").strip()
    if not text:
        return None
    cfg = get_bench_configuration_for_stored_value(getattr(forward.efiling, "bench", None))
    if not cfg or len(tuple(cfg.judge_groups or ())) <= 1:
        return forward.listing_summary
    brg = (getattr(forward, "bench_role_group", None) or "").strip()
    if brg:
        try:
            role = resolve_bench_role_group_for_forward(user, forward.bench_key)
        except ValueError:
            return None
        return forward.listing_summary if brg == str(role) else None
    fwd_uid = getattr(getattr(forward, "forwarded_by", None), "id", None)
    if fwd_uid is None:
        return forward.listing_summary
    judge_ids = list(JudgeT.objects.filter(user_id=user.id).values_list("id", flat=True))
    if not judge_ids:
        return None
    reader_ids = set(
        ReaderJudgeAssignment.objects.filter(judge_id__in=judge_ids).values_list(
            "reader_user_id", flat=True
        )
    )
    if int(fwd_uid) in reader_ids:
        return forward.listing_summary
    return None


def _pick_forward_row_for_efiling_bench(
    user: User,
    efiling_id: int,
    bench_key: str,
) -> CourtroomForward | None:
    """
    Latest forward for efiling+bench, preferring the row that matches this judge's slot
    (same logic as the main pending list).
    """
    fs = list(
        CourtroomForward.objects.filter(efiling_id=efiling_id, bench_key=bench_key)
        .select_related("efiling")
        .prefetch_related("efiling__litigants")
        .order_by("-forwarded_for_date", "-id")
    )
    if not fs:
        return None
    matches = [x for x in fs if _courtroom_forward_matches_judge_slot(user, x)]
    if matches:
        return max(matches, key=lambda x: x.id)
    return None


def _forwards_from_published_cause_lists_for_date(
    *,
    cause_list_date,
    user: User,
    is_judge: bool,
) -> List[CourtroomForward]:
    """
    Courtroom / cause-list hearing day is keyed by **published** CauseList.cause_list_date,
    not CourtroomForward.forwarded_for_date. Resolves the display forward per efiling+bench.
    """
    entries = (
        CauseListEntry.objects.filter(
            cause_list__cause_list_date=cause_list_date,
            cause_list__status=CauseList.CauseListStatus.PUBLISHED,
            included=True,
        )
        .select_related("cause_list", "efiling")
    )
    seen_fwd: Set[int] = set()
    out: List[CourtroomForward] = []
    for ent in entries:
        eid = int(ent.efiling_id)
        bkey = str(ent.cause_list.bench_key)
        if is_judge:
            if not _judge_can_view_forward(user, bkey):
                continue
            cand = _pick_forward_row_for_efiling_bench(user, eid, bkey)
        else:
            cand = (
                CourtroomForward.objects.filter(efiling_id=eid, bench_key=bkey)
                .select_related("efiling")
                .prefetch_related("efiling__litigants")
                .order_by("-forwarded_for_date", "-id")
                .first()
            )
        if cand and cand.id not in seen_fwd:
            out.append(cand)
            seen_fwd.add(cand.id)
    out.sort(key=lambda x: -x.id)
    return out


def _pick_courtroom_forward_for_user(
    user: User,
    f_qs,
    *,
    is_judge: bool,
) -> CourtroomForward | None:
    ordered = list(f_qs.order_by("-forwarded_for_date", "-id"))
    if not ordered:
        return None
    if not is_judge:
        return ordered[0]
    for cand in ordered:
        if _courtroom_forward_matches_judge_slot(user, cand):
            return cand
    return None


def _resolve_courtroom_forward_for_hearing_day(
    user: User,
    efiling_id: int,
    *,
    hearing_date,
    forward_bench_key: str | None,
    is_judge: bool,
) -> CourtroomForward | None:
    """
    Match the **cause-list / hearing calendar day** (``CauseList.cause_list_date``), not necessarily
    ``CourtroomForward.forwarded_for_date``. Used by case summary and documents when the reader
    forwarded on a different day than the published list date.
    """
    base = (
        CourtroomForward.objects.filter(efiling_id=efiling_id)
        .select_related("efiling")
        .prefetch_related("efiling__litigants")
    )
    if is_judge:
        allowed_bench_keys = _bench_key_aliases_list_for_judge(user)
        base = base.filter(bench_key__in=allowed_bench_keys)
    if forward_bench_key:
        base = base.filter(bench_key=forward_bench_key)

    if hearing_date is None:
        return _pick_courtroom_forward_for_user(user, base, is_judge=is_judge)

    strict = base.filter(forwarded_for_date=hearing_date)
    forward = _pick_courtroom_forward_for_user(user, strict, is_judge=is_judge)
    if forward:
        return forward

    ent_qs = CauseListEntry.objects.filter(
        efiling_id=efiling_id,
        included=True,
        cause_list__cause_list_date=hearing_date,
        cause_list__status=CauseList.CauseListStatus.PUBLISHED,
    ).select_related("cause_list")
    if forward_bench_key:
        ent_qs = ent_qs.filter(cause_list__bench_key=forward_bench_key)
    entries = list(ent_qs.order_by("-id"))

    def _fallback_latest() -> CourtroomForward | None:
        return _pick_courtroom_forward_for_user(
            user, base.order_by("-forwarded_for_date", "-id"), is_judge=is_judge
        )

    if not entries:
        return _fallback_latest()

    for ent in entries:
        bkey = str(ent.cause_list.bench_key)
        if is_judge:
            if not _judge_can_view_forward(user, bkey):
                continue
            cand = _pick_forward_row_for_efiling_bench(user, efiling_id, bkey)
        else:
            cand = (
                CourtroomForward.objects.filter(efiling_id=efiling_id, bench_key=bkey)
                .select_related("efiling")
                .prefetch_related("efiling__litigants")
                .order_by("-forwarded_for_date", "-id")
                .first()
            )
        if cand:
            return cand

    return _fallback_latest()


def _efiling_ids_listed_for_another_hearing_day(hearing_date) -> Set[int]:
    """
    E-filing IDs whose official hearing day (Listing Officer cause list, any status,
    or reader ``listing_date`` on a judge decision with remark) is set to a calendar
    day **other than** ``hearing_date``. Pre-publish courtroom rows must not appear
    on the wrong day when ``CourtroomForward.forwarded_for_date`` still matches an
    earlier reader forward.
    """
    other_cl = CauseListEntry.objects.filter(included=True).exclude(
        cause_list__cause_list_date=hearing_date
    )
    from_decision = CourtroomJudgeDecision.objects.filter(
        listing_date__isnull=False,
    ).exclude(listing_date=hearing_date)
    from_decision = from_decision.filter(
        ~Q(reader_listing_remark__isnull=True) & ~Q(reader_listing_remark__exact="")
    )
    return set(other_cl.values_list("efiling_id", flat=True)) | set(
        from_decision.values_list("efiling_id", flat=True)
    )


class CourtroomPendingCasesView(APIView):
    """
    Pending courtroom cases for a **hearing / cause-list calendar day**.

    Query params (either): ``cause_list_date`` (preferred) or ``forwarded_for_date`` (alias).
    The **published** bucket is driven by ``CauseList.cause_list_date`` for **PUBLISHED** lists,
    not by ``CourtroomForward.forwarded_for_date``.

    Judges: ``pending_for_causelist`` = published cause list for that day; ``pending_for_listing``
    = reader forwards dated that calendar day that are not yet published for this day, and not
    already assigned to another hearing day (cause list or reader ``listing_date``).

    Advocates: only published rows for that cause-list date.
    """

    def get(self, request, *args, **kwargs):
        user = _resolve_courtroom_user(request)
        user_groups = _user_judge_groups(user)
        is_judge = bool(user_groups)

        date_raw = request.query_params.get("cause_list_date") or request.query_params.get(
            "forwarded_for_date"
        )
        if date_raw:
            hearing_date = timezone.datetime.fromisoformat(date_raw).date()
        else:
            hearing_date = timezone.now().date()

        # Published cause list entries for this hearing calendar day
        listed_efiling_ids = set(
            CauseListEntry.objects.filter(
                cause_list__cause_list_date=hearing_date,
                cause_list__status=CauseList.CauseListStatus.PUBLISHED,
                included=True,
            ).values_list("efiling_id", flat=True)
        )

        # Advocates have nothing to see until something is on a published list for that date.
        if not is_judge and not listed_efiling_ids:
            return Response({"pending_for_listing": [], "pending_for_causelist": []}, status=drf_status.HTTP_200_OK)

        if is_judge:
            forwards_published = _forwards_from_published_cause_lists_for_date(
                cause_list_date=hearing_date,
                user=user,
                is_judge=True,
            )
            # Pre-publish: reader forward rows for this calendar day, excluding efilings
            # already on the published cause list for this hearing day, and efilings whose
            # official listing day is another calendar date (LO list or reader listing_date).
            listed_on_other_day = _efiling_ids_listed_for_another_hearing_day(hearing_date)
            base_pre = CourtroomForward.objects.filter(forwarded_for_date=hearing_date)
            raw_pre = list(
                base_pre.select_related("efiling")
                .prefetch_related("efiling__litigants")
                .order_by("-id")
            )
            by_efiling: Dict[int, List[CourtroomForward]] = {}
            for f in raw_pre:
                if not _judge_can_view_forward(user, f.bench_key):
                    continue
                if f.efiling_id in listed_efiling_ids:
                    continue
                if f.efiling_id in listed_on_other_day:
                    continue
                by_efiling.setdefault(f.efiling_id, []).append(f)
            forwards_pre: List[CourtroomForward] = []
            for _eid, fs in by_efiling.items():
                matches = [x for x in fs if _courtroom_forward_matches_judge_slot(user, x)]
                if matches:
                    forwards_pre.append(max(matches, key=lambda x: x.id))
            forwards_pre.sort(key=lambda x: -x.id)
            forwards = forwards_published + forwards_pre
        else:
            forwards = _forwards_from_published_cause_lists_for_date(
                cause_list_date=hearing_date,
                user=user,
                is_judge=False,
            )

        if not is_judge:
            accessible_ids = set(EfilerDocumentAccess.objects.filter(efiler=user).values_list("e_filing_id", flat=True))
            creator_ids = set(Efiling.objects.filter(created_by=user).values_list("id", flat=True))
            accessible_ids.update(creator_ids)
            if user.email == "dummy_advocate@hcs.local":
                accessible_ids.update(listed_efiling_ids)

        def build_item(
            f: CourtroomForward,
            *,
            courtroom_bucket: str | None = None,
        ) -> dict:
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
                "petitioner_name": getattr(f.efiling, "petitioner_name", None),
                "petitioner_vs_respondent": getattr(
                    f.efiling, "petitioner_vs_respondent_display", "-"
                ),
                "filing_date": (
                    getattr(f.efiling, "filing_date", None).isoformat()
                    if getattr(f.efiling, "filing_date", None)
                    else None
                ),
                "cause_list_date": hearing_date.isoformat(),
                "listing_summary": (
                    _listing_summary_visible_to_judge(user, f)
                    if is_judge
                    else f.listing_summary
                ),
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

            if courtroom_bucket:
                item["courtroom_bucket"] = courtroom_bucket

            return item

        pending_for_listing: List[dict] = []
        pending_for_causelist: List[dict] = []
        seen_pre: Set[int] = set()
        seen_pub: Set[int] = set()

        for f in forwards:
            if is_judge:
                if not _judge_can_view_forward(user, f.bench_key):
                    continue
            else:
                if f.efiling_id not in accessible_ids:
                    continue

            on_published_list = f.efiling_id in listed_efiling_ids

            if is_judge:
                if on_published_list:
                    if f.efiling_id in seen_pub:
                        continue
                    seen_pub.add(f.efiling_id)
                    pending_for_causelist.append(
                        build_item(f, courtroom_bucket="published_causelist")
                    )
                else:
                    if f.efiling_id in seen_pre:
                        continue
                    seen_pre.add(f.efiling_id)
                    pending_for_listing.append(
                        build_item(f, courtroom_bucket="pre_publish_listing")
                    )
            else:
                if f.efiling_id in seen_pub:
                    continue
                seen_pub.add(f.efiling_id)
                pending_for_causelist.append(
                    build_item(f, courtroom_bucket="published_causelist")
                )

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
        date_raw = request.query_params.get("cause_list_date") or request.query_params.get(
            "forwarded_for_date"
        )
        forward_bench_key = str(request.query_params.get("forward_bench_key") or "").strip() or None

        # 1. Permission and Publication Check
        access_meta = _validate_courtroom_access(
            user,
            efiling_id,
            date_raw,
            allow_judge_unpublished=True,
        )
        is_judge = access_meta.get("is_judge", False)

        hearing_date = None
        if date_raw:
            hearing_date = timezone.datetime.fromisoformat(date_raw).date()

        forward = _resolve_courtroom_forward_for_hearing_day(
            user,
            efiling_id,
            hearing_date=hearing_date,
            forward_bench_key=forward_bench_key,
            is_judge=is_judge,
        )

        if not forward:
            raise ValidationError({"detail": "Case forward record not found."})

        requested_only = str(request.query_params.get("requested_only", "")).strip().lower() in {"1", "true", "yes", "y"}

        doc_indexes_qs = EfilingDocumentsIndex.objects.filter(
            document__e_filing_id=efiling_id, is_active=True
        ).select_related("document", "document__e_filing").order_by(
            "document_sequence",
            "parent_document_index_id",
            "id",
        )
        
        # SYNC MODIFICATION: Only show documents specifically selected for the hearing (Hearing Pack).
        # Exception: approved case-access vakalatnamas should remain visible in case files.
        selected_ids = list(forward.selected_documents.values_list("efiling_document_index_id", flat=True))
        if selected_ids:
            access_vakalat_ids = list(
                doc_indexes_qs.filter(
                    Q(document__document_type__icontains="vakalat")
                    | Q(document_part_name__icontains="vakalatnama - ")
                ).values_list("id", flat=True)
            )
            visible_ids = set(selected_ids) | set(access_vakalat_ids)
            doc_indexes_qs = doc_indexes_qs.filter(id__in=visible_ids)

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

        filing = Efiling.objects.filter(id=efiling_id).only("id", "case_number", "e_filing_number").first()
        return Response(
            {
                "items": doc_items,
                "orders": _orders_for_efiling(request, filing) if filing else [],
            },
            status=drf_status.HTTP_200_OK,
        )


class CourtroomCaseSummaryView(APIView):
    """
    Unified: get case summary details.
    """

    def get(self, request, efiling_id: int, *args, **kwargs):
        user = _resolve_courtroom_user(request)
        date_raw = request.query_params.get("cause_list_date") or request.query_params.get(
            "forwarded_for_date"
        )
        forward_bench_key = str(request.query_params.get("forward_bench_key") or "").strip() or None

        # 1. Permission and Publication Check
        access_meta = _validate_courtroom_access(
            user,
            efiling_id,
            date_raw,
            allow_judge_unpublished=True,
        )
        is_judge = access_meta.get("is_judge", False)

        hearing_date = None
        if date_raw:
            hearing_date = timezone.datetime.fromisoformat(date_raw).date()

        forward = _resolve_courtroom_forward_for_hearing_day(
            user,
            efiling_id,
            hearing_date=hearing_date,
            forward_bench_key=forward_bench_key,
            is_judge=is_judge,
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
                "forwarded_for_date": forward.forwarded_for_date.isoformat(),
                "listing_summary": (
                    _listing_summary_visible_to_judge(user, forward)
                    if is_judge
                    else forward.listing_summary
                ),
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
                "orders": _orders_for_efiling(request, filing),
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

        allowed_bench_keys = _bench_key_aliases_list_for_judge(user)
        if not CourtroomForward.objects.filter(
            efiling_id=doc_index.document.e_filing_id,
            bench_key__in=allowed_bench_keys,
        ).exists():
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
        status = CourtroomJudgeDecision.DecisionStatus.APPROVED
        requested_document_index_ids = payload.validated_data.get("requested_document_index_ids") or []
        approved = True
        decision_notes = payload.validated_data.get("decision_notes")
        # Ensure there is an authorized forward row and resolve an unambiguous
        # bench role slot for this decision.
        fwd_qs = CourtroomForward.objects.filter(
            efiling_id=efiling_id,
            forwarded_for_date=forwarded_for_date,
        )
        if forward_bench_key:
            fwd_qs = fwd_qs.filter(bench_key=forward_bench_key)
        candidate_forwards = list(fwd_qs.order_by("-id"))
        if not candidate_forwards:
            raise ValidationError({"detail": "Case not forwarded for this date."})
        resolved_candidates: list[tuple[CourtroomForward, str]] = []
        for fwd in candidate_forwards:
            if not _judge_can_view_forward(user, fwd.bench_key):
                continue
            try:
                role_group = resolve_bench_role_group_for_forward(user, fwd.bench_key)
            except ValueError:
                continue
            brg = (getattr(fwd, "bench_role_group", None) or "").strip()
            if brg and brg != str(role_group):
                continue
            resolved_candidates.append((fwd, role_group))

        if not resolved_candidates:
            raise ValidationError(
                {
                    "detail": (
                        "Unable to resolve judge role slot for this bench. "
                        "Configure bench seating (JudgeT) or bench slot groups for this forward."
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
            # when users only have the generic JUDGE group.
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
        judge_user = _assert_judge(request)
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
            if not _judge_can_view_forward(judge_user, getattr(row.proceeding, "bench_key", None)):
                continue
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
        if not _judge_can_view_forward(judge_user, getattr(workflow.proceeding, "bench_key", None)):
            raise ValidationError({"detail": "Not authorized for this workflow."})
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
        if not _judge_can_view_forward(judge_user, getattr(workflow.proceeding, "bench_key", None)):
            raise ValidationError({"detail": "Not authorized for this workflow."})
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
        if not _judge_can_view_forward(judge_user, getattr(workflow.proceeding, "bench_key", None)):
            raise ValidationError({"detail": "Not authorized for this workflow."})
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


class JudgeBenchAccessDebugView(APIView):
    """
    Judge-only diagnostics to verify bench seating/slot resolution.
    Useful when validating cross-visibility issues in live roster data.
    """

    def get(self, request, *args, **kwargs):
        user = _assert_judge(request)

        aliases = _bench_key_aliases_list_for_judge(user)
        forwards = (
            CourtroomForward.objects.filter(bench_key__in=aliases, is_active=True)
            .values_list("bench_key", flat=True)
            .distinct()
        )
        bench_keys = sorted(set(aliases) | {str(x) for x in forwards if x})

        seat_resolution: list[dict[str, Any]] = []
        for bench_key in bench_keys:
            required = list(get_required_judge_groups(bench_key))
            try:
                resolved = resolve_bench_role_group_for_forward(user, bench_key)
                seat_resolution.append(
                    {
                        "bench_key": bench_key,
                        "required_groups": required,
                        "resolved_group": resolved,
                        "can_view_forward": _judge_can_view_forward(user, bench_key),
                    }
                )
            except ValueError as exc:
                seat_resolution.append(
                    {
                        "bench_key": bench_key,
                        "required_groups": required,
                        "resolved_group": None,
                        "can_view_forward": _judge_can_view_forward(user, bench_key),
                        "resolution_error": str(exc),
                    }
                )

        return Response(
            {
                "judge_user_id": user.id,
                "judge_email": user.email,
                "judge_groups": sorted(
                    list(user.groups.values_list("name", flat=True))
                ),
                "bench_key_aliases": aliases,
                "seat_resolution": seat_resolution,
            },
            status=drf_status.HTTP_200_OK,
        )
