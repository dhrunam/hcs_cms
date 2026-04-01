from django.db import models


class PaymentTransaction(models.Model):
    payment_type = models.CharField(max_length=30, blank=True, null=True)
    payment_mode = models.CharField(max_length=20, blank=True, null=True)
    application = models.CharField(max_length=120, blank=True, null=True)
    txn_id = models.CharField(max_length=120, blank=True, null=True)
    reference_no = models.CharField(max_length=120, blank=True, null=True)
    status = models.CharField(max_length=60, blank=True, null=True)
    amount = models.CharField(max_length=40, blank=True, null=True)
    court_fees = models.CharField(max_length=40, blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)
    bank_receipt = models.FileField(upload_to="payment/", blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    callback_method = models.CharField(max_length=10, blank=True, null=True)
    callback_payload = models.JSONField(default=dict, blank=True)
    redirect_url = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_transaction"
        ordering = ["-created_at"]

