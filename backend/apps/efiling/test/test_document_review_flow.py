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

    def test_review_status_propagates_through_full_flow(self):
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
        self.assertEqual(self.filing.status, "REJECTED")
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.REJECTED)

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
        self.assertEqual(self.filing.status, "ACCEPTED")
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED)
        self.assertGreaterEqual(document_index.scrutiny_history.count(), 5)

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

    def test_rejected_status_is_not_reset_by_review_list_endpoint(self):
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
        self.assertEqual(document_index.scrutiny_status, EfilingDocumentsIndex.ScrutinyStatus.REJECTED)
