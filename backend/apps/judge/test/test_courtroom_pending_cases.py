"""
Courtroom pending cases: judges can see pre-publish forwarded summaries;
advocates only after publish. Case-open access for judges remains publish-gated.
"""

from datetime import timedelta

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.core.models import BenchT, Efiling, JudgeT, ReaderJudgeAssignment
from apps.judge.models import CourtroomJudgeDecision, JUDGE_GROUP_CJ
from apps.listing.models import CauseList, CauseListEntry
from apps.reader.models import CourtroomForward


class CourtroomPendingCasesViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.forwarded_for_date = timezone.localdate()

        self.judge_user = User.objects.create_user(
            email="pending.judge@example.com",
            username="pending_judge",
            password="password123",
        )
        grp_cj, _ = Group.objects.get_or_create(name=JUDGE_GROUP_CJ)
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")
        self.judge_user.groups.add(grp_cj, grp_j)

        self.judge_t = JudgeT.objects.create(
            user=self.judge_user,
            judge_code="PEND-J",
            judge_name="Pending Judge",
            display="PJ",
            date_of_joining=self.forwarded_for_date,
        )
        BenchT.objects.create(
            bench_code="PEND1",
            bench_name="Pending Bench",
            bench_type_code="S",
            judge_code=self.judge_t.judge_code,
            judge=self.judge_t,
            from_date=self.forwarded_for_date,
        )

        self.advocate_user = User.objects.create_user(
            email="pending.advocate@example.com",
            username="pending_advocate",
            password="password123",
        )

        self.filing = Efiling.objects.create(
            case_number="PENDING-CL-001",
            e_filing_number="ASK20260000001C202600099",
            bench="PEND1",
            petitioner_name="Petitioner",
            petitioner_contact="9876543210",
            is_draft=False,
            status="ACCEPTED",
            created_by=self.advocate_user,
        )

        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="PEND1",
            bench_role_group="BENCH_S0",
            listing_summary="Reader summary text",
            forwarded_by=self.judge_user,
        )

    def _url(self):
        d = self.forwarded_for_date.isoformat()
        return f"/api/v1/judge/courtroom/pending/?forwarded_for_date={d}"

    def test_judge_sees_pre_publish_forward_in_pending_for_listing(self):
        self.client.force_authenticate(user=self.judge_user)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["pending_for_listing"]), 1)
        self.assertEqual(len(resp.data["pending_for_causelist"]), 0)
        self.assertEqual(resp.data["pending_for_listing"][0]["efiling_id"], self.filing.id)
        self.assertEqual(
            resp.data["pending_for_listing"][0]["listing_summary"],
            "Reader summary text",
        )

    def test_advocate_empty_when_nothing_published(self):
        self.client.force_authenticate(user=self.advocate_user)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["pending_for_listing"], [])
        self.assertEqual(resp.data["pending_for_causelist"], [])

    def test_judge_buckets_after_publish(self):
        cause_list = CauseList.objects.create(
            cause_list_date=self.forwarded_for_date,
            bench_key="PEND1",
            status=CauseList.CauseListStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        CauseListEntry.objects.create(
            cause_list=cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )

        self.client.force_authenticate(user=self.judge_user)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["pending_for_listing"]), 0)
        self.assertEqual(len(resp.data["pending_for_causelist"]), 1)
        self.assertEqual(resp.data["pending_for_causelist"][0]["efiling_id"], self.filing.id)

    def test_judge_sees_published_cause_when_forward_date_not_hearing_date(self):
        """Hearing date matches cause list; reader forward may use an earlier calendar day."""
        hearing = self.forwarded_for_date
        old_date = hearing - timedelta(days=10)
        CourtroomForward.objects.filter(efiling=self.filing).update(
            forwarded_for_date=old_date
        )
        cause_list = CauseList.objects.create(
            cause_list_date=hearing,
            bench_key="PEND1",
            status=CauseList.CauseListStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        CauseListEntry.objects.create(
            cause_list=cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )

        self.client.force_authenticate(user=self.judge_user)
        resp = self.client.get(
            f"/api/v1/judge/courtroom/pending/?forwarded_for_date={hearing.isoformat()}"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["pending_for_causelist"]), 1)
        self.assertEqual(resp.data["pending_for_causelist"][0]["efiling_id"], self.filing.id)
        self.assertEqual(
            resp.data["pending_for_causelist"][0]["courtroom_bucket"],
            "published_causelist",
        )

    def test_pre_publish_hidden_when_draft_cause_list_on_different_day(self):
        """LO draft list for a later day must not let the case appear on an earlier reader-forward day."""
        early = self.forwarded_for_date
        late = self.forwarded_for_date + timedelta(days=7)
        cl = CauseList.objects.create(
            cause_list_date=late,
            bench_key="PEND1",
            status=CauseList.CauseListStatus.DRAFT,
        )
        CauseListEntry.objects.create(
            cause_list=cl,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )
        self.client.force_authenticate(user=self.judge_user)
        resp = self.client.get(
            f"/api/v1/judge/courtroom/pending/?cause_list_date={early.isoformat()}"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["pending_for_listing"], [])
        self.assertEqual(resp.data["pending_for_causelist"], [])

    def test_pre_publish_hidden_when_reader_listing_date_on_other_day(self):
        """Reader listing_date (with remark) on another day excludes pre-publish on this day."""
        early = self.forwarded_for_date
        late = self.forwarded_for_date + timedelta(days=7)
        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge_user,
            efiling=self.filing,
            forwarded_for_date=early,
            listing_date=late,
            reader_listing_remark="Listed for next week",
        )
        self.client.force_authenticate(user=self.judge_user)
        resp = self.client.get(
            f"/api/v1/judge/courtroom/pending/?cause_list_date={early.isoformat()}"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["pending_for_listing"], [])
        self.assertEqual(resp.data["pending_for_causelist"], [])

    def test_published_still_visible_on_assigned_day_when_forward_earlier(self):
        """Published cause list for day D lists the case even if reader forward is on an earlier day."""
        early = self.forwarded_for_date
        late = self.forwarded_for_date + timedelta(days=7)
        CourtroomForward.objects.filter(efiling=self.filing).update(forwarded_for_date=early)
        cause_list = CauseList.objects.create(
            cause_list_date=late,
            bench_key="PEND1",
            status=CauseList.CauseListStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        CauseListEntry.objects.create(
            cause_list=cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )
        self.client.force_authenticate(user=self.judge_user)
        resp = self.client.get(
            f"/api/v1/judge/courtroom/pending/?cause_list_date={late.isoformat()}"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["pending_for_causelist"]), 1)
        self.assertEqual(resp.data["pending_for_causelist"][0]["efiling_id"], self.filing.id)

    def test_judge_case_summary_allowed_before_publish(self):
        self.client.force_authenticate(user=self.judge_user)
        url = (
            f"/api/v1/judge/courtroom/cases/{self.filing.id}/summary/"
            f"?forwarded_for_date={self.forwarded_for_date.isoformat()}"
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_judge_case_documents_allowed_before_publish(self):
        self.client.force_authenticate(user=self.judge_user)
        url = (
            f"/api/v1/judge/courtroom/cases/{self.filing.id}/documents/"
            f"?forwarded_for_date={self.forwarded_for_date.isoformat()}"
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_judge_case_summary_allowed_after_publish(self):
        cause_list = CauseList.objects.create(
            cause_list_date=self.forwarded_for_date,
            bench_key="PEND1",
            status=CauseList.CauseListStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        CauseListEntry.objects.create(
            cause_list=cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )
        self.client.force_authenticate(user=self.judge_user)
        url = (
            f"/api/v1/judge/courtroom/cases/{self.filing.id}/summary/"
            f"?forwarded_for_date={self.forwarded_for_date.isoformat()}"
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_advocate_sees_case_after_publish(self):
        cause_list = CauseList.objects.create(
            cause_list_date=self.forwarded_for_date,
            bench_key="PEND1",
            status=CauseList.CauseListStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        CauseListEntry.objects.create(
            cause_list=cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )

        self.client.force_authenticate(user=self.advocate_user)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["pending_for_listing"], [])
        self.assertEqual(len(resp.data["pending_for_causelist"]), 1)
        self.assertEqual(resp.data["pending_for_causelist"][0]["efiling_id"], self.filing.id)

    def test_advocate_case_summary_when_forward_date_not_hearing_date(self):
        """Cause-list day may differ from CourtroomForward.forwarded_for_date; summary must still load."""
        hearing = self.forwarded_for_date
        old_date = hearing - timedelta(days=10)
        CourtroomForward.objects.filter(efiling=self.filing).update(forwarded_for_date=old_date)
        cause_list = CauseList.objects.create(
            cause_list_date=hearing,
            bench_key="PEND1",
            status=CauseList.CauseListStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        CauseListEntry.objects.create(
            cause_list=cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )
        self.client.force_authenticate(user=self.advocate_user)
        url = (
            f"/api/v1/judge/courtroom/cases/{self.filing.id}/summary/"
            f"?forwarded_for_date={hearing.isoformat()}"
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["efiling_id"], self.filing.id)
        self.assertEqual(resp.data["forwarded_for_date"], old_date.isoformat())

    def test_judge_on_different_bench_sees_no_cases(self):
        other = User.objects.create_user(
            email="pending.judge2@example.com",
            username="pending_judge2",
            password="password123",
        )
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")
        other.groups.add(grp_j)
        other_jt = JudgeT.objects.create(
            user=other,
            judge_code="PEND-J2",
            judge_name="Other Bench Judge",
            display="PJ2",
            date_of_joining=self.forwarded_for_date,
        )
        BenchT.objects.create(
            bench_code="PEND2",
            bench_name="Other Pending Bench",
            bench_type_code="S",
            judge_code=other_jt.judge_code,
            judge=other_jt,
            from_date=self.forwarded_for_date,
        )

        self.client.force_authenticate(user=other)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["pending_for_listing"], [])
        self.assertEqual(resp.data["pending_for_causelist"], [])

    def test_judge_on_different_bench_sees_no_cases_after_publish(self):
        cause_list = CauseList.objects.create(
            cause_list_date=self.forwarded_for_date,
            bench_key="PEND1",
            status=CauseList.CauseListStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        CauseListEntry.objects.create(
            cause_list=cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )

        other = User.objects.create_user(
            email="pending.judge3@example.com",
            username="pending_judge3",
            password="password123",
        )
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")
        other.groups.add(grp_j)
        other_jt = JudgeT.objects.create(
            user=other,
            judge_code="PEND-J3",
            judge_name="Other Bench Judge 3",
            display="PJ3",
            date_of_joining=self.forwarded_for_date,
        )
        BenchT.objects.create(
            bench_code="PEND3",
            bench_name="Other Pending Bench 3",
            bench_type_code="S",
            judge_code=other_jt.judge_code,
            judge=other_jt,
            from_date=self.forwarded_for_date,
        )

        self.client.force_authenticate(user=other)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["pending_for_listing"], [])
        self.assertEqual(resp.data["pending_for_causelist"], [])

    def test_published_cause_lists_for_seated_judge_filters_bench(self):
        cause_list = CauseList.objects.create(
            cause_list_date=self.forwarded_for_date,
            bench_key="PEND1",
            status=CauseList.CauseListStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        CauseListEntry.objects.create(
            cause_list=cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )

        url = (
            f"/api/v1/listing/cause-lists/published/?cause_list_date="
            f"{self.forwarded_for_date.isoformat()}&for_seated_judge=true"
        )
        self.client.force_authenticate(user=self.judge_user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["items"]), 1)
        self.assertEqual(resp.data["items"][0]["bench_key"], "PEND1")

        other = User.objects.create_user(
            email="pending.judge4@example.com",
            username="pending_judge4",
            password="password123",
        )
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")
        other.groups.add(grp_j)
        other_jt = JudgeT.objects.create(
            user=other,
            judge_code="PEND-J4",
            judge_name="Other Bench Judge 4",
            display="PJ4",
            date_of_joining=self.forwarded_for_date,
        )
        BenchT.objects.create(
            bench_code="PEND4",
            bench_name="Other Pending Bench 4",
            bench_type_code="S",
            judge_code=other_jt.judge_code,
            judge=other_jt,
            from_date=self.forwarded_for_date,
        )
        self.client.force_authenticate(user=other)
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.data["items"], [])


class DivisionBenchJudgeListingSummaryVisibilityTest(TestCase):
    """Division bench pre-publish forwards are visible only to the judge served by that reader."""

    def setUp(self):
        self.client = APIClient()
        self.d = timezone.localdate()
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")

        self.reader_a = User.objects.create_user(
            email="div.reader.a@example.com",
            username="div_reader_a",
            password="password123",
        )
        self.reader_b = User.objects.create_user(
            email="div.reader.b@example.com",
            username="div_reader_b",
            password="password123",
        )

        self.judge_a = User.objects.create_user(
            email="div.judge.a@example.com",
            username="div_judge_a",
            password="password123",
        )
        self.judge_b = User.objects.create_user(
            email="div.judge.b@example.com",
            username="div_judge_b",
            password="password123",
        )
        self.judge_a.groups.add(grp_j)
        self.judge_b.groups.add(grp_j)

        self.jt_a = JudgeT.objects.create(
            user=self.judge_a,
            judge_code="DIV-JA",
            judge_name="Judge A",
            display="JA",
            date_of_joining=self.d,
        )
        self.jt_b = JudgeT.objects.create(
            user=self.judge_b,
            judge_code="DIV-JB",
            judge_name="Judge B",
            display="JB",
            date_of_joining=self.d,
        )

        ReaderJudgeAssignment.objects.create(
            judge=self.jt_a,
            reader_user=self.reader_a,
            effective_from=self.d,
        )
        ReaderJudgeAssignment.objects.create(
            judge=self.jt_b,
            reader_user=self.reader_b,
            effective_from=self.d,
        )

        BenchT.objects.create(
            bench_code="DIVX",
            bench_name="Division Visibility Bench",
            bench_type_code="DB",
            judge_code=self.jt_a.judge_code,
            judge=self.jt_a,
            from_date=self.d,
        )
        BenchT.objects.create(
            bench_code="DIVX",
            bench_name="Division Visibility Bench",
            bench_type_code="DB",
            judge_code=self.jt_b.judge_code,
            judge=self.jt_b,
            from_date=self.d,
        )

        self.filing = Efiling.objects.create(
            case_number="DIV-VIS-001",
            e_filing_number="ASK20260000001C202600501",
            bench="DIVX",
            petitioner_name="Petitioner",
            petitioner_contact="9876543210",
            is_draft=False,
            status="ACCEPTED",
        )
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.d,
            bench_key="DIVX",
            bench_role_group="BENCH_S0",
            listing_summary="Reader A confidential summary",
            forwarded_by=self.reader_a,
        )

    def _pending_items(self, user: User):
        self.client.force_authenticate(user=user)
        url = f"/api/v1/judge/courtroom/pending/?forwarded_for_date={self.d.isoformat()}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        return (resp.data.get("pending_for_listing") or []) + (
            resp.data.get("pending_for_causelist") or []
        )

    def test_pre_publish_forward_visible_only_to_reader_mapped_judge(self):
        items_a = self._pending_items(self.judge_a)
        self.assertEqual(len(items_a), 1)
        self.assertEqual(items_a[0].get("listing_summary"), "Reader A confidential summary")

        items_b = self._pending_items(self.judge_b)
        self.assertEqual(items_b, [])
