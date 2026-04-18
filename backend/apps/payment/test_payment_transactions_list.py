"""List API returns all payment rows for an application, newest first."""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.payment.models import PaymentTransaction


class PaymentTransactionsListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_returns_newest_first(self):
        app_id = "99901"
        older = PaymentTransaction.objects.create(
            application=app_id,
            payment_mode="online",
            reference_no="REF_OLD",
            status="success",
            amount="100",
        )
        newer = PaymentTransaction.objects.create(
            application=app_id,
            payment_mode="online",
            reference_no="REF_NEW",
            status="success",
            amount="200",
        )
        response = self.client.get(
            "/api/payment/transactions/",
            {"application": app_id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 2)
        ids = [r["id"] for r in data["results"]]
        self.assertEqual(ids[0], newer.id)
        self.assertEqual(ids[1], older.id)
        self.assertEqual(data["results"][0]["reference_no"], "REF_NEW")

    def test_list_empty_application(self):
        response = self.client.get(
            "/api/payment/transactions/",
            {"application": "no_such_app"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_list_requires_application(self):
        response = self.client.get("/api/payment/transactions/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
