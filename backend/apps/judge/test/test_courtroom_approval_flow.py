"""bench_role_group + shared approval helpers."""

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import Efiling
from apps.judge.courtroom_approval import efiling_ids_with_all_required_approvals
from apps.judge.models import CourtroomJudgeDecision
from apps.reader.models import CourtroomForward


class CourtroomApprovalFlowTest(TestCase):
    def setUp(self):
        self.fwd_date = timezone.localdate()
        self.judge = User.objects.create_user(
            email="flow.judge@example.com",
            username="flow_judge",
            password="x",
        )
        grp, _ = Group.objects.get_or_create(name="API_JUDGE")
        self.judge.groups.add(grp)

        self.filing = Efiling.objects.create(
            case_number="FLOW-001",
            e_filing_number="ASK20260000001C202600201",
            bench="CJ",
            petitioner_name="P",
            petitioner_contact="1",
            is_draft=False,
            status="ACCEPTED",
        )
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.fwd_date,
            bench_key="CJ",
            listing_summary="Summary",
            forwarded_by=self.judge,
        )

    def test_api_judge_approval_counts_when_bench_role_set(self):
        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge,
            efiling=self.filing,
            forwarded_for_date=self.fwd_date,
            approved=True,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            bench_role_group="JUDGE_CJ",
        )
        out = efiling_ids_with_all_required_approvals(
            bench_key="CJ",
            efiling_ids=[self.filing.id],
            forwarded_for_date=self.fwd_date,
            listing_date=None,
        )
        self.assertEqual(out, {self.filing.id})

    def test_decision_view_persists_bench_role_group_single_bench(self):
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.judge)
        resp = client.post(
            "/api/v1/judge/courtroom/decisions/",
            {
                "efiling_id": self.filing.id,
                "forwarded_for_date": self.fwd_date.isoformat(),
                "decision_notes": "approved",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        row = CourtroomJudgeDecision.objects.get(
            judge_user=self.judge,
            efiling=self.filing,
            forwarded_for_date=self.fwd_date,
        )
        self.assertEqual(row.bench_role_group, "JUDGE_CJ")
