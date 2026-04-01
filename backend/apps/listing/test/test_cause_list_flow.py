from django.test import TestCase
from rest_framework.test import APIClient

from apps.core.models import District, Efiling, EfilingCaseDetails, EfilingLitigant, State
from apps.listing.models import CauseList


class CauseListFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cause_list_date = "2026-03-25"

        self.filing = Efiling.objects.create(
            case_number="CASE-TEST-001",
            e_filing_number="ASK20240000001C202400001",
            bench="CJ",
            petitioner_name="Petitioner",
            petitioner_contact="9876543210",
            is_draft=False,
            status="ACCEPTED",
        )

        # Respondent litigant (used by /registered-cases endpoint)
        self.respondent_litigant = EfilingLitigant.objects.create(
            e_filing=self.filing,
            name="Respondent",
            is_petitioner=False,
            sequence_number=2,
        )

        # Case details (used by /registered-cases endpoint)
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
        save_payload = {
            "cause_list_date": self.cause_list_date,
            "bench_key": "CJ",
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
        # Smoke-check key text exists in the generated PDF bytes.
        self.assertIn(b"THE HIGH COURT OF SIKKIM", pdf_bytes)
        self.assertIn(b"DAILY CAUSELIST", pdf_bytes)
        self.assertIn(b"HON'BLE THE CHIEF JUSTICE", pdf_bytes)

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
        self.assertEqual(entry_resp.data["bench_key"], "CJ")
        self.assertEqual(entry_resp.data["serial_no"], 1)
        self.assertIsNotNone(entry_resp.data["pdf_url"])

    def test_registered_cases_and_assign_benches_flow(self):
        # 1) Listing officer fetches registered cases
        resp = self.client.get("/api/v1/listing/registered-cases/?page_size=10")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data["total"] >= 1)

        item = next((i for i in resp.data["items"] if i["efiling_id"] == self.filing.id), None)
        self.assertIsNotNone(item)
        self.assertEqual(item["case_number"], self.filing.case_number)
        self.assertEqual(item["petitioner_name"], "Petitioner")
        self.assertEqual(item["respondent_name"], "Respondent")
        self.assertIn("Petitioner", item.get("petitioner_vs_respondent") or "")
        self.assertIn("Respondent", item.get("petitioner_vs_respondent") or "")

        # 2) Assign the case to full bench
        assign_resp = self.client.post(
            "/api/v1/listing/registered-cases/assign-bench/",
            {
                "assignments": [
                    {"efiling_id": self.filing.id, "bench_key": "CJ+Judge1+Judge2"},
                ]
            },
            format="json",
        )
        self.assertEqual(assign_resp.status_code, 200)
        self.assertEqual(assign_resp.data["updated"], 1)

        self.filing.refresh_from_db()
        self.assertEqual(self.filing.bench, "CJ+Judge1+Judge2")

        # 3) Generator preview should now include it under the assigned bench
        preview_resp = self.client.get(
            f"/api/v1/listing/cause-lists/draft/preview/?cause_list_date={self.cause_list_date}&bench_key=CJ+Judge1+Judge2"
        )
        self.assertEqual(preview_resp.status_code, 200)
        preview_items = preview_resp.data["items"]
        self.assertTrue(any(i["efiling_id"] == self.filing.id for i in preview_items))

