from datetime import date, timedelta

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.core.models import BenchT, District, Efiling, EfilingCaseDetails, EfilingLitigant, JudgeT, State
from apps.judge.models import CourtroomJudgeDecision
from apps.listing.models import CauseList
from apps.reader.models import CourtroomForward


class CauseListFlowTest(TestCase):
    """Cause list flows use active BenchT buckets (bench_code) and authenticated listing users."""

    def setUp(self):
        self.client = APIClient()
        self.cause_list_date = "2026-03-25"
        self.cause_date = date.fromisoformat(self.cause_list_date)

        self.listing_user = User.objects.create_user(
            email="listing.officer@example.com",
            username="listing_officer_cl",
            password="testpass123",
        )
        grp_lo, _ = Group.objects.get_or_create(name="LISTING_OFFICER")
        self.listing_user.groups.add(grp_lo)
        self.client.force_authenticate(user=self.listing_user)

        grp_judge, _ = Group.objects.get_or_create(name="JUDGE")
        self.judge_user = User.objects.create_user(
            email="cl.judge1@example.com",
            username="cl_judge1",
            password="testpass123",
        )
        self.judge_user.groups.add(grp_judge)
        self.judge_t = JudgeT.objects.create(
            user=self.judge_user,
            judge_code="CL-J1",
            judge_name="Cause List Judge One",
            display="CLJ1",
            date_of_joining=date(2020, 1, 1),
        )
        BenchT.objects.create(
            bench_code="CLTEST",
            bench_name="Cause List Test Bench",
            bench_type_code="S",
            judge_code=self.judge_t.judge_code,
            judge=self.judge_t,
            from_date=date(2020, 1, 1),
        )

        self.judge2_user = User.objects.create_user(
            email="cl.judge2@example.com",
            username="cl_judge2",
            password="testpass123",
        )
        self.judge2_user.groups.add(grp_judge)
        self.judge_t2 = JudgeT.objects.create(
            user=self.judge2_user,
            judge_code="CL-J2",
            judge_name="Cause List Judge Two",
            display="CLJ2",
            date_of_joining=date(2020, 1, 1),
        )
        BenchT.objects.create(
            bench_code="CLTEST2",
            bench_name="Cause List Test Bench Two",
            bench_type_code="S",
            judge_code=self.judge_t2.judge_code,
            judge=self.judge_t2,
            from_date=date(2020, 1, 1),
        )

        self.filing = Efiling.objects.create(
            case_number="CASE-TEST-001",
            e_filing_number="ASK20240000001C202400001",
            bench="CLTEST",
            petitioner_name="Petitioner",
            petitioner_contact="9876543210",
            is_draft=False,
            status="ACCEPTED",
        )

        self.respondent_litigant = EfilingLitigant.objects.create(
            e_filing=self.filing,
            name="Respondent",
            is_petitioner=False,
            sequence_number=2,
        )

        self.state = State.objects.create(est_code_src="S1")
        self.district = District.objects.create()

        EfilingCaseDetails.objects.create(
            e_filing=self.filing,
            cause_of_action="Test cause of action",
            date_of_cause_of_action="2026-01-01",
            dispute_state=self.state,
            dispute_district=self.district,
            dispute_taluka="Test Taluka",
        )

    def test_publish_sets_status_and_creates_pdf(self):
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.cause_date,
            bench_key="CLTEST",
            bench_role_group="BENCH_S0",
            listing_summary="Reader forwarded for publish",
        )

        save_payload = {
            "cause_list_date": self.cause_list_date,
            "bench_key": "CLTEST",
            "entries": [
                {
                    "efiling_id": self.filing.id,
                    "serial_no": 1,
                    "included": True,
                }
            ],
        }

        save_resp = self.client.post("/api/v1/listing/cause-lists/draft/save/", save_payload, format="json")
        self.assertEqual(save_resp.status_code, 200)
        cause_list_id = save_resp.data["cause_list_id"]

        publish_resp = self.client.post(f"/api/v1/listing/cause-lists/{cause_list_id}/publish/", {}, format="json")
        self.assertEqual(publish_resp.status_code, 200)
        self.assertEqual(publish_resp.data["status"], CauseList.CauseListStatus.PUBLISHED)
        self.assertIsNotNone(publish_resp.data["pdf_url"])

        cl = CauseList.objects.get(pk=cause_list_id)
        self.assertEqual(cl.status, CauseList.CauseListStatus.PUBLISHED)
        self.assertTrue(bool(cl.pdf_file))
        with cl.pdf_file.open("rb") as f:
            pdf_bytes = f.read()
        # Text is typically inside Flate-compressed streams; smoke-check structure only.
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 5000)

        published_resp = self.client.get(
            f"/api/v1/listing/cause-lists/published/?cause_list_date={self.cause_list_date}"
        )
        self.assertEqual(published_resp.status_code, 200)
        self.assertEqual(len(published_resp.data["items"]), 1)

        entry_resp = self.client.get(
            f"/api/v1/listing/cause-lists/entry/?cause_list_date={self.cause_list_date}&case_number={self.filing.case_number}"
        )
        self.assertEqual(entry_resp.status_code, 200)
        self.assertTrue(entry_resp.data["found"])
        self.assertEqual(entry_resp.data["bench_key"], "CLTEST")
        self.assertEqual(entry_resp.data["serial_no"], 1)
        self.assertIsNotNone(entry_resp.data["pdf_url"])

    def test_registered_cases_and_assign_benches_flow(self):
        resp = self.client.get("/api/v1/listing/registered-cases/?page_size=10")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data["total"] >= 1)

        item = next((i for i in resp.data["items"] if i["efiling_id"] == self.filing.id), None)
        self.assertIsNotNone(item)
        self.assertEqual(item["case_number"], self.filing.case_number)
        self.assertEqual(item["petitioner_name"], "Petitioner")
        self.assertEqual(item["respondent_name"], "Respondent")
        self.assertIn("Petitioner", item.get("petitioner_vs_respondent") or "")

        assign_resp = self.client.post(
            "/api/v1/listing/registered-cases/assign-bench/",
            {
                "assignments": [
                    {"efiling_id": self.filing.id, "bench_key": "CLTEST2"},
                ]
            },
            format="json",
        )
        self.assertEqual(assign_resp.status_code, 200)
        self.assertEqual(assign_resp.data["updated"], 1)

        self.filing.refresh_from_db()
        self.assertEqual(self.filing.bench, "CLTEST2")

        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.cause_date,
            bench_key="CLTEST2",
            bench_role_group="BENCH_S0",
            listing_summary="Reader forwarded after assign",
        )

        preview_resp = self.client.get(
            f"/api/v1/listing/cause-lists/draft/preview/?cause_list_date={self.cause_list_date}&bench_key=CLTEST2"
        )
        self.assertEqual(preview_resp.status_code, 200)
        preview_items = preview_resp.data["items"]
        self.assertTrue(any(i["efiling_id"] == self.filing.id for i in preview_items))

    def test_listing_preview_needs_reader_handoff_for_judge_listing_data(self):
        self.filing.bench = "CLTEST"
        self.filing.save(update_fields=["bench"])

        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.cause_date,
            bench_key="CLTEST",
            bench_role_group="BENCH_S0",
            listing_summary="Reader forwarded",
        )
        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge_user,
            efiling=self.filing,
            forwarded_for_date=self.cause_date,
            listing_date=None,
            approved=True,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            bench_role_group="BENCH_S0",
        )

        preview_resp = self.client.get(
            f"/api/v1/listing/cause-lists/draft/preview/?cause_list_date={self.cause_list_date}&bench_key=CLTEST"
        )
        self.assertEqual(preview_resp.status_code, 200)
        preview_items = preview_resp.data["items"]
        item = next((i for i in preview_items if i["efiling_id"] == self.filing.id), None)
        self.assertIsNotNone(item)
        self.assertIsNone(item.get("judge_listing_date"))

    def test_draft_preview_falls_back_to_bench_workflow_state_listing_date(self):
        """When judge decision has no listing_date, listing officer still sees reader-synced date."""
        from apps.reader.models import BenchWorkflowState

        self.filing.bench = "CLTEST"
        self.filing.save(update_fields=["bench"])
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.cause_date,
            bench_key="CLTEST",
            bench_role_group="BENCH_S0",
            listing_summary="Reader forwarded",
        )
        next_hearing = self.cause_date + timedelta(days=21)
        BenchWorkflowState.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.cause_date,
            bench_key="CLTEST",
            required_role_groups=["BENCH_S0"],
            decision_by_role={},
            listing_date=next_hearing,
            listing_remark="Reader proceedings next date",
        )
        preview_resp = self.client.get(
            f"/api/v1/listing/cause-lists/draft/preview/?cause_list_date={self.cause_list_date}&bench_key=CLTEST"
        )
        self.assertEqual(preview_resp.status_code, 200)
        item = next(
            (i for i in (preview_resp.data.get("items") or []) if i["efiling_id"] == self.filing.id),
            None,
        )
        self.assertIsNotNone(item)
        self.assertEqual(item.get("judge_listing_date"), next_hearing.isoformat())
        self.assertEqual(item.get("reader_listing_remark"), "Reader proceedings next date")

    def test_draft_preview_includes_reader_next_listing_date_cases(self):
        other_day = self.cause_date + timedelta(days=1)
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=other_day,
            bench_key="CLTEST",
            bench_role_group="BENCH_S0",
            listing_summary="Forwarded for another day",
        )
        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge_user,
            efiling=self.filing,
            forwarded_for_date=other_day,
            listing_date=self.cause_date,
            reader_listing_remark="Different date listing",
            approved=True,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            bench_role_group="BENCH_S0",
        )
        preview_resp = self.client.get(
            f"/api/v1/listing/cause-lists/draft/preview/?cause_list_date={self.cause_list_date}&bench_key=CLTEST"
        )
        self.assertEqual(preview_resp.status_code, 200)
        preview_ids = {int(item["efiling_id"]) for item in (preview_resp.data.get("items") or [])}
        self.assertIn(self.filing.id, preview_ids)

    def test_published_list_returns_benchwise_rows_for_date(self):
        CauseList.objects.create(
            cause_list_date=self.cause_date,
            bench_key="CLTEST",
            status=CauseList.CauseListStatus.PUBLISHED,
        )
        CauseList.objects.create(
            cause_list_date=self.cause_date,
            bench_key="CLTEST2",
            status=CauseList.CauseListStatus.PUBLISHED,
        )
        resp = self.client.get(
            f"/api/v1/listing/cause-lists/published/?cause_list_date={self.cause_list_date}"
        )
        self.assertEqual(resp.status_code, 200)
        items = resp.data.get("items") or []
        self.assertEqual(len(items), 2)
