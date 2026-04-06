"""IA filing mandatory court fee (Rs. 10) — payment_transaction.application reference."""
from decimal import Decimal, InvalidOperation

from django.conf import settings

from apps.payment.models import PaymentTransaction

IA_COURT_FEE_AMOUNT = Decimal("10.00")
IA_COURT_FEE_PAYMENT_TYPE = "IA Court Fee"


def normalize_ia_status(value):
    if value is None or str(value).strip() == "":
        return ""
    return str(value).strip().upper().replace(" ", "_")


def ia_fee_application_ref(ia_id: int) -> str:
    return f"IA-FEE-{ia_id}"


def ia_court_fee_payment_satisfied(ia_id: int) -> bool:
    """True if there is a successful payment row for this IA with amount >= Rs. 10."""
    if not ia_id:
        return False
    ref = ia_fee_application_ref(ia_id)
    pg = getattr(settings, "PG_PAYMENT_STATUS", None) or {}
    success_status = str(pg.get("success", "success")).lower()
    qs = (
        PaymentTransaction.objects.filter(
            application=ref,
        )
        .filter(payment_type__iexact=IA_COURT_FEE_PAYMENT_TYPE)
        .order_by("-updated_at", "-id")
    )
    for tx in qs:
        if str(tx.status or "").lower() != success_status:
            continue
        raw = str(tx.amount or tx.court_fees or "0").strip()
        try:
            if Decimal(raw) >= IA_COURT_FEE_AMOUNT:
                return True
        except (InvalidOperation, TypeError, ValueError):
            continue
    return False
