from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.core.models import CaseTypeT, Efiling, EfilingDocuments
from apps.payment.models import PaymentTransaction


class EfilingDocumentSubmitFilingViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="submit-filing-user",
            email="submit-filing@example.com",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)
        self.case_type = CaseTypeT.objects.create(
            case_type=1,
            type_name="WP",
            type_flag="C",
            est_code_src="ASK001",
            reg_no=0,
            reg_year=0,
        )
        self.filing = Efiling.objects.create(
            case_type=self.case_type,
            petitioner_name="Test Petitioner",
            petitioner_contact="9876543210",
            bench="Principal Bench",
            is_draft=False,
        )
        self.doc = EfilingDocuments.objects.create(
            e_filing=self.filing,
            e_filing_number=self.filing.e_filing_number,
            document_type="Additional Document",
            is_ia=False,
        )

    def test_submit_fails_without_matching_payment(self):
        url = f"/api/v1/efiling/efiling-documents/{self.doc.id}/submit-filing/"
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_returns_404_when_document_id_does_not_exist(self):
        url = "/api/v1/efiling/efiling-documents/999999999/submit-filing/"
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_submit_inactive_without_payment_returns_400(self):
        self.doc.is_active = False
        self.doc.save(update_fields=["is_active"])
        url = f"/api/v1/efiling/efiling-documents/{self.doc.id}/submit-filing/"
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_succeeds_when_payment_matches_document(self):
        self.doc.is_active = False
        self.doc.save(update_fields=["is_active"])
        payment_status = getattr(
            settings,
            "PG_PAYMENT_STATUS",
            {"initiated": "initiated", "success": "success", "failed": "failed"},
        )
        success_label = payment_status.get("success", "success")
        PaymentTransaction.objects.create(
            payment_type="Court Fees",
            payment_mode="offline",
            application=str(self.filing.id),
            reference_no="REF-SUBMIT-TEST-1",
            txn_id="TXN-1",
            amount="100",
            court_fees="100",
            status=success_label,
            message="ok",
            callback_method="OFFLINE",
            callback_payload={
                "application": str(self.filing.id),
                "e_filing_number": self.filing.e_filing_number or "",
                "source": "document_filing",
                "efiling_document_id": self.doc.id,
            },
        )
        url = f"/api/v1/efiling/efiling-documents/{self.doc.id}/submit-filing/"
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("document_id"), self.doc.id)
        self.doc.refresh_from_db()
        self.assertIsNotNone(self.doc.document_filing_submitted_at)
        self.assertTrue(self.doc.is_active)

    def test_post_document_with_pending_flag_sets_inactive(self):
        url = "/api/v1/efiling/efiling-documents/"
        response = self.client.post(
            url,
            {
                "document_type": "Annexure",
                "e_filing": self.filing.id,
                "e_filing_number": self.filing.e_filing_number or "",
                "is_ia": "false",
                "pending_until_document_filing_submit": "true",
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc_id = response.data.get("id")
        self.assertIsNotNone(doc_id)
        row = EfilingDocuments.objects.get(pk=doc_id)
        self.assertFalse(row.is_active)

    def test_submit_idempotent_without_payment_when_already_submitted(self):
        self.doc.document_filing_submitted_at = timezone.now()
        self.doc.save(update_fields=["document_filing_submitted_at"])
        url = f"/api/v1/efiling/efiling-documents/{self.doc.id}/submit-filing/"
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("document_id"), self.doc.id)
