from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Efiling, EfilingDocuments, EfilingDocumentsIndex


class DocumentReviewFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.filing = Efiling.objects.create(
            petitioner_name="Test Petitioner",
            petitioner_contact="9876543210",
            bench="Principal Bench",
        )

    def upload_document(self, name="petition.pdf", content=b"%PDF-1.4 petition"):
        payload = {
            "e_filing": self.filing.id,
            "e_filing_number": self.filing.e_filing_number,
            "document_type": "Main Petition",
            "final_document": SimpleUploadedFile(name, content, content_type="application/pdf"),
        }
        return self.client.post("/api/v1/efiling/efiling-documents/", payload, format="multipart")

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
        self.assertEqual(self.filing.status, "ACCEPTED")
        self.assertIsNotNone(self.filing.case_number)
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED)
        self.assertIsNone(document_index.draft_scrutiny_status)
        self.assertGreaterEqual(document_index.scrutiny_history.count(), 4)

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
