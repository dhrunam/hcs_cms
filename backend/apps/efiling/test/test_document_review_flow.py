from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.core.models import CaseTypeT, Efiling, EfilingDocuments, EfilingDocumentsIndex


@override_settings(EFILING_VALIDATE_PDF_UPLOAD=False)
class DocumentReviewFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="document-review-user",
            email="document-review@example.com",
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
        self.filing = self.create_filing()

    def create_filing(self, **overrides):
        payload = {
            "petitioner_name": "Test Petitioner",
            "petitioner_contact": "9876543210",
            "bench": "Principal Bench",
            "case_type": self.case_type,
        }
        payload.update(overrides)
        return Efiling.objects.create(**payload)

    def upload_document(self, filing=None, name="petition.pdf", content=b"%PDF-1.4 petition"):
        filing = filing or self.filing
        payload = {
            "e_filing": filing.id,
            "e_filing_number": filing.e_filing_number,
            "document_type": "Main Petition",
            "final_document": SimpleUploadedFile(name, content, content_type="application/pdf"),
        }
        return self.client.post("/api/v1/efiling/efiling-documents/", payload, format="multipart")

    def prepare_filing_for_approval(self, filing=None):
        filing = filing or self.filing
        upload_response = self.upload_document(filing=filing)
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)

        document = EfilingDocuments.objects.filter(e_filing=filing).order_by("-id").first()
        document_index = EfilingDocumentsIndex.objects.get(document=document)

        submit_response = self.client.patch(
            f"/api/v1/efiling/efilings/{filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)

        accept_response = self.client.patch(
            f"/api/v1/efiling/efiling-documents-index/{document_index.id}/",
            {
                "scrutiny_status": EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
                "comments": "Accepted for registration.",
            },
            format="json",
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        return document, document_index

    def test_review_status_changes_are_draft_until_final_submit(self):
        upload_response = self.upload_document()
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)

        document = EfilingDocuments.objects.get()
        document_index = EfilingDocumentsIndex.objects.get(document=document)
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.DRAFT)
        self.assertEqual(document_index.scrutiny_history.count(), 1)

        submit_response = self.client.patch(
            f"/api/v1/efiling/efilings/{self.filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)

        self.filing.refresh_from_db()
        document_index.refresh_from_db()
        self.assertFalse(self.filing.is_draft)
        self.assertEqual(self.filing.status, "UNDER_SCRUTINY")
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY)
        self.assertTrue(document_index.is_new_for_scrutiny)

        reject_response = self.client.patch(
            f"/api/v1/efiling/efiling-documents-index/{document_index.id}/",
            {
                "scrutiny_status": EfilingDocumentsIndex.ScrutinyStatus.REJECTED,
                "comments": "Please re-upload a clearer PDF.",
            },
            format="json",
        )
        self.assertEqual(reject_response.status_code, status.HTTP_200_OK)

        self.filing.refresh_from_db()
        document_index.refresh_from_db()
        self.assertEqual(self.filing.status, "UNDER_SCRUTINY")
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY)
        self.assertEqual(
            document_index.draft_scrutiny_status,
            EfilingDocumentsIndex.ScrutinyStatus.REJECTED,
        )
        self.assertEqual(document_index.draft_comments, "Please re-upload a clearer PDF.")

        replace_response = self.client.patch(
            f"/api/v1/efiling/efiling-documents/{document.id}/",
            {
                "document_type": "Main Petition",
                "final_document": SimpleUploadedFile(
                    "petition-replaced.pdf",
                    b"%PDF-1.4 replacement",
                    content_type="application/pdf",
                ),
            },
            format="multipart",
        )
        self.assertEqual(replace_response.status_code, status.HTTP_200_OK)

        self.filing.refresh_from_db()
        document_index.refresh_from_db()
        self.assertEqual(self.filing.status, "UNDER_SCRUTINY")
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY)
        self.assertIsNone(document_index.draft_scrutiny_status)
        self.assertTrue(document_index.is_new_for_scrutiny)

        accept_response = self.client.patch(
            f"/api/v1/efiling/efiling-documents-index/{document_index.id}/",
            {
                "scrutiny_status": EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
                "comments": "Accepted after replacement.",
            },
            format="json",
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)

        self.filing.refresh_from_db()
        document_index.refresh_from_db()
        self.assertEqual(self.filing.status, "UNDER_SCRUTINY")
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY)
        self.assertEqual(
            document_index.draft_scrutiny_status,
            EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
        )
        submit_response = self.client.post(
            f"/api/v1/efiling/efilings/{self.filing.id}/submit-approved/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        self.filing.refresh_from_db()
        document_index.refresh_from_db()
        self.case_type.refresh_from_db()
        current_year = self.filing.accepted_at.year
        self.assertEqual(self.filing.status, "ACCEPTED")
        self.assertEqual(self.filing.case_number, f"WP/1/{current_year}")
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED)
        self.assertIsNone(document_index.draft_scrutiny_status)
        self.assertGreaterEqual(document_index.scrutiny_history.count(), 4)
        self.assertEqual(self.case_type.reg_no, 1)
        self.assertEqual(self.case_type.reg_year, current_year)

    def test_document_replace_is_blocked_until_rejected(self):
        self.upload_document()
        document = EfilingDocuments.objects.get()
        document_index = EfilingDocumentsIndex.objects.get(document=document)

        self.client.patch(
            f"/api/v1/efiling/efilings/{self.filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )
        document_index.refresh_from_db()
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY)

        blocked_response = self.client.patch(
            f"/api/v1/efiling/efiling-documents/{document.id}/",
            {
                "document_type": "Main Petition",
                "final_document": SimpleUploadedFile(
                    "petition-blocked.pdf",
                    b"%PDF-1.4 blocked",
                    content_type="application/pdf",
                ),
            },
            format="multipart",
        )
        self.assertEqual(blocked_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_replacing_rejected_review_item_returns_it_to_scrutiny(self):
        self.upload_document()
        document = EfilingDocuments.objects.get()
        primary_index = EfilingDocumentsIndex.objects.get(document=document)

        self.client.patch(
            f"/api/v1/efiling/efilings/{self.filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )

        secondary_index = EfilingDocumentsIndex.objects.create(
            document=document,
            document_part_name="Annexure",
            file_part_path=primary_index.file_part_path.name,
            document_sequence=(primary_index.document_sequence or 1) + 1,
            scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            is_new_for_scrutiny=False,
        )

        self.client.patch(
            f"/api/v1/efiling/efiling-documents-index/{primary_index.id}/",
            {
                "scrutiny_status": EfilingDocumentsIndex.ScrutinyStatus.REJECTED,
                "comments": "Main petition is blurred.",
            },
            format="json",
        )

        replace_response = self.client.patch(
            f"/api/v1/efiling/efiling-documents-index/{primary_index.id}/",
            {
                "file_part_path": SimpleUploadedFile(
                    "petition-fixed.pdf",
                    b"%PDF-1.4 replacement",
                    content_type="application/pdf",
                ),
            },
            format="multipart",
        )
        self.assertEqual(replace_response.status_code, status.HTTP_200_OK)

        self.filing.refresh_from_db()
        primary_index.refresh_from_db()
        secondary_index.refresh_from_db()

        self.assertEqual(self.filing.status, "UNDER_SCRUTINY")
        self.assertEqual(primary_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY)
        self.assertIsNone(primary_index.draft_scrutiny_status)
        self.assertTrue(primary_index.is_new_for_scrutiny)
        self.assertEqual(secondary_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED)
        self.assertFalse(secondary_index.is_new_for_scrutiny)
        self.assertIsNone(secondary_index.draft_scrutiny_status)

    def test_review_endpoints_filter_by_filing_and_document_index(self):
        self.upload_document()
        document = EfilingDocuments.objects.get()
        document_index = EfilingDocumentsIndex.objects.get(document=document)

        self.client.patch(
            f"/api/v1/efiling/efilings/{self.filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )

        documents_response = self.client.get(
            f"/api/v1/efiling/efiling-documents-index/?efiling_id={self.filing.id}"
        )
        self.assertEqual(documents_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(documents_response.data["results"]), 1)

        history_response = self.client.get(
            f"/api/v1/efiling/efiling-documents-scrutiny-history/?document_index_id={document_index.id}"
        )
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(history_response.data["results"]), 1)

    def test_review_endpoint_backfills_existing_documents_without_index(self):
        upload_response = self.upload_document()
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)

        document = EfilingDocuments.objects.get()
        EfilingDocumentsIndex.objects.filter(document=document).delete()

        self.client.patch(
            f"/api/v1/efiling/efilings/{self.filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )

        response = self.client.get(
            f"/api/v1/efiling/efiling-documents-index/?efiling_id={self.filing.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertTrue(EfilingDocumentsIndex.objects.filter(document=document).exists())

    def test_draft_rejected_status_is_not_reset_by_review_list_endpoint(self):
        self.upload_document()
        document = EfilingDocuments.objects.get()
        document_index = EfilingDocumentsIndex.objects.get(document=document)

        self.client.patch(
            f"/api/v1/efiling/efilings/{self.filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )
        self.client.patch(
            f"/api/v1/efiling/efiling-documents-index/{document_index.id}/",
            {
                "scrutiny_status": EfilingDocumentsIndex.ScrutinyStatus.REJECTED,
                "comments": "Rejected for replacement.",
            },
            format="json",
        )

        list_response = self.client.get(
            f"/api/v1/efiling/efiling-documents-index/?efiling_id={self.filing.id}"
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        document_index.refresh_from_db()
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY)
        self.assertEqual(document_index.draft_scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.REJECTED)

    def test_submit_with_any_rejected_marks_filing_rejected(self):
        self.upload_document()
        document = EfilingDocuments.objects.get()
        primary_index = EfilingDocumentsIndex.objects.get(document=document)
        secondary_index = EfilingDocumentsIndex.objects.create(
            document=document,
            document_part_name="Annexure",
            file_part_path=primary_index.file_part_path.name,
            document_sequence=(primary_index.document_sequence or 1) + 1,
            scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY,
            is_active=True,
        )

        self.client.patch(
            f"/api/v1/efiling/efilings/{self.filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )
        self.client.patch(
            f"/api/v1/efiling/efiling-documents-index/{primary_index.id}/",
            {"scrutiny_status": EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED, "comments": "ok"},
            format="json",
        )
        self.client.patch(
            f"/api/v1/efiling/efiling-documents-index/{secondary_index.id}/",
            {"scrutiny_status": EfilingDocumentsIndex.ScrutinyStatus.REJECTED, "comments": "fix this"},
            format="json",
        )

        submit_response = self.client.post(
            f"/api/v1/efiling/efilings/{self.filing.id}/submit-approved/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)

        self.filing.refresh_from_db()
        primary_index.refresh_from_db()
        secondary_index.refresh_from_db()
        self.assertEqual(self.filing.status, "PARTIALLY_REJECTED")
        self.assertIsNone(self.filing.case_number)
        self.assertEqual(primary_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED)
        self.assertEqual(secondary_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.REJECTED)
        self.assertIsNone(primary_index.draft_scrutiny_status)
        self.assertIsNone(secondary_index.draft_scrutiny_status)

    def test_submit_requires_all_documents_reviewed(self):
        self.upload_document()
        document = EfilingDocuments.objects.get()
        document_index = EfilingDocumentsIndex.objects.get(document=document)
        self.client.patch(
            f"/api/v1/efiling/efilings/{self.filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )
        self.assertEqual(document_index.draft_scrutiny_status, None)

        submit_response = self.client.post(
            f"/api/v1/efiling/efilings/{self.filing.id}/submit-approved/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_document_index_created_after_registration_is_sent_for_scrutiny(self):
        self.upload_document()
        document = EfilingDocuments.objects.get()
        document_index = EfilingDocumentsIndex.objects.get(document=document)

        self.client.patch(
            f"/api/v1/efiling/efilings/{self.filing.id}/",
            {"is_draft": "false"},
            format="multipart",
        )
        self.client.patch(
            f"/api/v1/efiling/efiling-documents-index/{document_index.id}/",
            {"scrutiny_status": EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED, "comments": "ok"},
            format="json",
        )
        submit_response = self.client.post(
            f"/api/v1/efiling/efilings/{self.filing.id}/submit-approved/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        self.filing.refresh_from_db()
        self.assertIsNotNone(self.filing.case_number)

        create_response = self.client.post(
            "/api/v1/efiling/efiling-documents-index/",
            {
                "document": document.id,
                "document_part_name": "Additional Affidavit",
                "file_part_path": SimpleUploadedFile(
                    "additional-affidavit.pdf",
                    b"%PDF-1.4 additional",
                    content_type="application/pdf",
                ),
                "document_sequence": 99,
            },
            format="multipart",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        new_index = EfilingDocumentsIndex.objects.order_by("-id").first()
        self.assertIsNotNone(new_index)
        self.assertEqual(new_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY)
        self.assertTrue(new_index.is_new_for_scrutiny)
        self.assertIsNotNone(new_index.last_resubmitted_at)

    def test_submit_approved_increments_registration_within_same_year(self):
        self.prepare_filing_for_approval(self.filing)
        first_submit = self.client.post(
            f"/api/v1/efiling/efilings/{self.filing.id}/submit-approved/",
            {},
            format="json",
        )
        self.assertEqual(first_submit.status_code, status.HTTP_200_OK)

        second_filing = self.create_filing(petitioner_name="Second Petitioner")
        self.prepare_filing_for_approval(second_filing)
        second_submit = self.client.post(
            f"/api/v1/efiling/efilings/{second_filing.id}/submit-approved/",
            {},
            format="json",
        )
        self.assertEqual(second_submit.status_code, status.HTTP_200_OK)

        self.filing.refresh_from_db()
        second_filing.refresh_from_db()
        self.case_type.refresh_from_db()
        current_year = self.case_type.reg_year

        self.assertEqual(self.filing.case_number, f"WP/1/{current_year}")
        self.assertEqual(second_filing.case_number, f"WP/2/{current_year}")
        self.assertEqual(self.case_type.reg_no, 2)

    def test_submit_approved_resets_registration_when_case_type_year_is_stale(self):
        current_year = self.filing.created_at.year
        self.case_type.reg_no = 7
        self.case_type.reg_year = current_year - 1
        self.case_type.save(update_fields=["reg_no", "reg_year", "updated_at"])

        self.prepare_filing_for_approval(self.filing)
        submit_response = self.client.post(
            f"/api/v1/efiling/efilings/{self.filing.id}/submit-approved/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)

        self.filing.refresh_from_db()
        self.case_type.refresh_from_db()
        self.assertEqual(self.filing.case_number, f"WP/1/{current_year}")
        self.assertEqual(self.case_type.reg_no, 1)
        self.assertEqual(self.case_type.reg_year, current_year)

    def test_submit_approved_is_idempotent_after_registration(self):
        self.prepare_filing_for_approval(self.filing)
        first_submit = self.client.post(
            f"/api/v1/efiling/efilings/{self.filing.id}/submit-approved/",
            {"bench": "Division Bench"},
            format="json",
        )
        self.assertEqual(first_submit.status_code, status.HTTP_200_OK)

        original_case_number = Efiling.objects.get(pk=self.filing.pk).case_number
        original_reg_no = CaseTypeT.objects.get(pk=self.case_type.pk).reg_no

        second_submit = self.client.post(
            f"/api/v1/efiling/efilings/{self.filing.id}/submit-approved/",
            {"bench": "Full Bench"},
            format="json",
        )
        self.assertEqual(second_submit.status_code, status.HTTP_200_OK)

        self.filing.refresh_from_db()
        self.case_type.refresh_from_db()
        self.assertEqual(self.filing.case_number, original_case_number)
        self.assertEqual(self.case_type.reg_no, original_reg_no)
        self.assertEqual(self.filing.bench, "Full Bench")

    def test_submit_approved_requires_case_type(self):
        filing = self.create_filing(case_type=None)
        self.prepare_filing_for_approval(filing)

        submit_response = self.client.post(
            f"/api/v1/efiling/efilings/{filing.id}/submit-approved/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Case type is required", str(submit_response.data))

    def test_submit_approved_requires_case_type_name(self):
        self.case_type.type_name = ""
        self.case_type.save(update_fields=["type_name", "updated_at"])
        self.prepare_filing_for_approval(self.filing)

        submit_response = self.client.post(
            f"/api/v1/efiling/efilings/{self.filing.id}/submit-approved/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Case type name is required", str(submit_response.data))
