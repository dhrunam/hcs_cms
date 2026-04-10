"""
Courtroom pending cases: judges can see pre-publish forwarded summaries;
advocates only after publish. Case-open access for judges remains publish-gated.
"""

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.core.models import Efiling
from apps.judge.models import JUDGE_GROUP_CJ
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
        group, _ = Group.objects.get_or_create(name=JUDGE_GROUP_CJ)
        self.judge_user.groups.add(group)

        self.advocate_user = User.objects.create_user(
            email="pending.advocate@example.com",
            username="pending_advocate",
            password="password123",
        )

        self.filing = Efiling.objects.create(
            case_number="PENDING-CL-001",
            e_filing_number="ASK20260000001C202600099",
            bench="CJ",
            petitioner_name="Petitioner",
            petitioner_contact="9876543210",
            is_draft=False,
            status="ACCEPTED",
            created_by=self.advocate_user,
        )

        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="CJ",
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
            bench_key="CJ",
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
            bench_key="CJ",
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
            bench_key="CJ",
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
