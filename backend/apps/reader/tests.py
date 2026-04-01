from datetime import timedelta

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.core.models import BenchT, Efiling, JudgeT, ReaderJudgeAssignment
from apps.judge.models import CourtroomJudgeDecision
from apps.reader.models import CourtroomForward


class ReaderDivisionBenchAuthorityTest(TestCase):
    def setUp(self):
        self.forwarded_for_date = timezone.localdate()
        self.listing_date = self.forwarded_for_date + timedelta(days=7)

        self.reader_cj = self._create_user(
            email="reader.cj@example.com",
            username="reader_cj",
            group_name="READER_CJ",
        )
        self.reader_j1 = self._create_user(
            email="reader.j1@example.com",
            username="reader_j1",
            group_name="READER_J1",
        )
        self.judge_cj_user = self._create_user(
            email="judge.cj@example.com",
            username="judge_cj",
            group_name="JUDGE_CJ",
        )
        self.judge_j1_user = self._create_user(
            email="judge.j1@example.com",
            username="judge_j1",
            group_name="JUDGE_J1",
        )

        self.judge_cj = JudgeT.objects.create(
            user=self.judge_cj_user,
            judge_code="SK0",
            judge_name="Chief Justice",
            display="Chief Justice",
            date_of_joining=self.forwarded_for_date,
        )
        self.judge_j1 = JudgeT.objects.create(
            user=self.judge_j1_user,
            judge_code="HSK0002",
            judge_name="Judge I",
            display="Judge I",
            date_of_joining=self.forwarded_for_date,
        )

        ReaderJudgeAssignment.objects.create(
            judge=self.judge_cj,
            reader_user=self.reader_cj,
            effective_from=self.forwarded_for_date,
        )
        ReaderJudgeAssignment.objects.create(
            judge=self.judge_j1,
            reader_user=self.reader_j1,
            effective_from=self.forwarded_for_date,
        )

        BenchT.objects.create(
            bench_code="DB1",
            bench_name="Division Bench I",
            bench_type_code="DB",
            judge_code=self.judge_cj.judge_code,
            judge=self.judge_cj,
            from_date=self.forwarded_for_date,
        )
        BenchT.objects.create(
            bench_code="DB1",
            bench_name="Division Bench I",
            bench_type_code="DB",
            judge_code=self.judge_j1.judge_code,
            judge=self.judge_j1,
            from_date=self.forwarded_for_date,
        )

        self.filing = Efiling.objects.create(
            case_number="DB-CASE-001",
            e_filing_number="ASK20260000001C202600001",
            bench="DB1",
            petitioner_name="Petitioner",
            petitioner_contact="9876543210",
            is_draft=False,
            status="ACCEPTED",
        )

        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="CJ",
            listing_summary="Division bench summary",
            forwarded_by=self.reader_cj,
        )
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="Judge1",
            listing_summary="Division bench summary",
            forwarded_by=self.reader_j1,
        )

        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge_cj_user,
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
        )
        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge_j1_user,
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
        )

    def _create_user(
        self,
        *,
        email: str,
        username: str,
        group_name: str,
    ) -> User:
        user = User.objects.create_user(
            email=email,
            username=username,
            password="password123",
            first_name=username,
            last_name="User",
        )
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        return user

    def _auth_client(self, user: User) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_lower_priority_reader_can_view_case_but_not_assign_date(self):
        client = self._auth_client(self.reader_j1)

        list_response = client.get(
            "/api/v1/reader/registered-cases/"
            "?page_size=10&reader_group=READER_J1"
        )

        self.assertEqual(list_response.status_code, 200)
        case_item = next(
            item
            for item in list_response.data["items"]
            if item["efiling_id"] == self.filing.id
        )
        self.assertEqual(case_item["approval_status"], "APPROVED")
        self.assertFalse(case_item["can_assign_listing_date"])

        assign_response = client.post(
            "/api/v1/reader/assign-date/?reader_group=READER_J1",
            {
                "efiling_ids": [self.filing.id],
                "listing_date": self.listing_date.isoformat(),
                "forwarded_for_date": self.forwarded_for_date.isoformat(),
                "listing_remark": "Attempt by lower-priority reader",
            },
            format="json",
        )

        self.assertEqual(assign_response.status_code, 400)
        self.assertIn(
            "higher-priority bench reader",
            assign_response.data["efiling_ids"][0],
        )
        self.assertFalse(
            CourtroomJudgeDecision.objects.filter(
                efiling=self.filing,
                forwarded_for_date=self.forwarded_for_date,
                listing_date__isnull=False,
            ).exists()
        )

    def test_higher_priority_reader_can_assign_date_for_division_bench(self):
        client = self._auth_client(self.reader_cj)

        list_response = client.get(
            "/api/v1/reader/registered-cases/"
            "?page_size=10&reader_group=READER_CJ"
        )

        self.assertEqual(list_response.status_code, 200)
        case_item = next(
            item
            for item in list_response.data["items"]
            if item["efiling_id"] == self.filing.id
        )
        self.assertTrue(case_item["can_assign_listing_date"])

        assign_response = client.post(
            "/api/v1/reader/assign-date/?reader_group=READER_CJ",
            {
                "efiling_ids": [self.filing.id],
                "listing_date": self.listing_date.isoformat(),
                "forwarded_for_date": self.forwarded_for_date.isoformat(),
                "listing_remark": "Final division bench date",
            },
            format="json",
        )

        self.assertEqual(assign_response.status_code, 200)
        self.assertEqual(assign_response.data["updated"], 2)
        self.assertEqual(
            CourtroomJudgeDecision.objects.filter(
                efiling=self.filing,
                forwarded_for_date=self.forwarded_for_date,
                listing_date=self.listing_date,
            ).count(),
            2,
        )
