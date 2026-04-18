import datetime
import hashlib
import os
import time
import uuid
from urllib.parse import urlencode

from django.core.files.storage import default_storage

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import IA
from apps.payment.models import PaymentTransaction


def _payment_transaction_dict(tx: PaymentTransaction, request) -> dict:
    return {
        "id": tx.id,
        "application": tx.application,
        "payment_type": tx.payment_type,
        "payment_mode": tx.payment_mode,
        "txn_id": tx.txn_id,
        "reference_no": tx.reference_no,
        "amount": tx.amount,
        "court_fees": tx.court_fees,
        "payment_date": (
            tx.payment_date.isoformat() if getattr(tx, "payment_date", None) else None
        ),
        "bank_receipt": (
            request.build_absolute_uri(tx.bank_receipt.url)
            if getattr(tx, "bank_receipt", None)
            else None
        ),
        "status": tx.status,
        "message": tx.message,
        "payment_datetime": tx.updated_at.isoformat() if tx.updated_at else None,
        "paid_at": tx.updated_at.isoformat() if tx.updated_at else None,
    }


def _merge_payment_callback_payload(existing, gateway_payload: dict) -> dict:
    """Keep initiate metadata (e.g. source) when storing the gateway response."""
    base = dict(existing) if isinstance(existing, dict) else {}
    if isinstance(gateway_payload, dict):
        base = {**base, **gateway_payload}
    return base


def generate_payment_reference_no():
    two_digit_year = datetime.datetime.now().year % 100
    month = datetime.datetime.now().month
    milliseconds = int(time.time() * 1000)
    return f"SHC{month:02d}{two_digit_year}{milliseconds}"


class PaymentInitiateView(APIView):
    """
    Build the POST payload for the external payment gateway (test / UAT).
    Frontend submits a generated HTML form to the gateway action URL.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        pg = settings.PG_PARAMS
        payment_status = getattr(
            settings,
            "PG_PAYMENT_STATUS",
            {"initiated": "initiated", "success": "success", "failed": "failed"},
        )
        amount = request.data.get("amount")
        application = request.data.get("application")
        e_filing_number = request.data.get("e_filing_number", "")
        payment_type = str(request.data.get("payment_type", "Court Fees"))
        source = str(request.data.get("source", "new_filing"))
        payee_name = str(request.data.get("payee_name", "Advocate"))

        if amount in (None, "", "0"):
            return Response({"detail": "Amount is required."}, status=400)
        if application in (None, ""):
            return Response({"detail": "Application id is required."}, status=400)

        reference_no = generate_payment_reference_no()
        encdata = self._create_encdata(reference_no, amount, payee_name, payment_type)

        raw_doc_id = request.data.get("efiling_document_id")
        efiling_document_id = None
        if raw_doc_id not in (None, ""):
            try:
                efiling_document_id = int(raw_doc_id)
            except (TypeError, ValueError):
                efiling_document_id = None

        callback_payload = {
            "application": str(application),
            "e_filing_number": str(e_filing_number or ""),
            "source": source,
            "encdata": encdata,
        }
        if efiling_document_id is not None:
            callback_payload["efiling_document_id"] = efiling_document_id

        PaymentTransaction.objects.create(
            payment_type=payment_type,
            payment_mode="online",
            application=str(application),
            reference_no=reference_no,
            status=payment_status.get("initiated", "initiated"),
            amount=str(amount),
            court_fees=str(amount),
            message="Initiated",
            callback_method="INIT",
<<<<<<< HEAD
            callback_payload={
                "application": str(application),
                "e_filing_number": str(e_filing_number or ""),
                "source": source,
                "encdata": encdata,
            },
            created_by=request.user if request.user.is_authenticated else None,
=======
            callback_payload=callback_payload,
>>>>>>> jwt-auth
        )

        fields = {"encdata": encdata}
        return Response(
            {
                "method": "POST",
                "action": pg.get("payment_request_url"),
                "fields": fields,
            }
        )

    def _create_checksum(self, ref_number, fee, payee_name, payment_type):
        pg = settings.PG_PARAMS
        base_string = (
            f"merchant_code={pg.get('merchant_code')}|"
            f"merchant_ref_no={ref_number}|"
            f"amount={fee}|"
            f"return_url={pg.get('return_url')}|"
            f"payee_name={payee_name}|"
            f"major_head_code={pg.get('major_head_code')}|"
            f"sub_major_head={pg.get('minor_head_code')}|"
            f"prod_desc={payment_type}|"
        )
        checksum_string = f"{base_string}salt={pg.get('salt')}"
        hash_object = hashlib.sha256()
        hash_object.update(checksum_string.encode("utf-8"))
        return {"base_string": base_string, "checkSum": hash_object.hexdigest()}

    def _create_encdata(self, ref_number, fee, payee_name, payment_type):
        checksum_dict = self._create_checksum(ref_number, fee, payee_name, payment_type)
        return f"{checksum_dict['base_string']}checkSum={checksum_dict['checkSum']}"

class PaymentGatewayConfigView(APIView):
    """
    Expose non-sensitive payment gateway config for test integration.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        pg_params = settings.PG_PARAMS
        return Response(
            {
                "merchant_code": pg_params.get("merchant_code"),
                "major_head_code": pg_params.get("major_head_code"),
                "minor_head_code": pg_params.get("minor_head_code"),
                "return_url": pg_params.get("return_url"),
                "payment_request_url": pg_params.get("payment_request_url"),
                "payment_status_url": pg_params.get("payment_status_url"),
            }
        )


class PaymentLatestTransactionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        application = request.query_params.get("application")
        if not application:
            return Response({"detail": "application is required."}, status=400)
        tx = (
            PaymentTransaction.objects.filter(application=str(application))
            .order_by("-updated_at", "-id")
            .first()
        )
        if not tx:
            return Response({}, status=200)
        return Response(
            {
                "application": tx.application,
                "payment_mode": tx.payment_mode,
                "txn_id": tx.txn_id,
                "reference_no": tx.reference_no,
                "amount": tx.amount,
                "court_fees": tx.court_fees,
                "payment_date": (
                    tx.payment_date.isoformat() if getattr(tx, "payment_date", None) else None
                ),
                "bank_receipt": (
                    request.build_absolute_uri(tx.bank_receipt.url)
                    if getattr(tx, "bank_receipt", None)
                    else None
                ),
                "status": tx.status,
                "message": tx.message,
                "payment_datetime": tx.updated_at.isoformat() if tx.updated_at else None,
                "paid_at": tx.updated_at.isoformat() if tx.updated_at else None,
            }
        )


class PaymentTransactionsListView(APIView):
    """
    All payment rows for a filing: same `application` as Efiling pk, plus IA court fees
    stored as `IA-FEE-{ia_id}` for IAs under that filing.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        application = request.query_params.get("application")
        if not application:
            return Response({"detail": "application is required."}, status=400)

        try:
            efiling_id = int(str(application).strip())
        except (TypeError, ValueError):
            efiling_id = None

        if efiling_id is not None:
            ia_refs = [
                f"IA-FEE-{pk}"
                for pk in IA.objects.filter(e_filing_id=efiling_id).values_list("id", flat=True)
            ]
            qs = PaymentTransaction.objects.filter(
                Q(application=str(efiling_id)) | Q(application__in=ia_refs)
            )
        else:
            qs = PaymentTransaction.objects.filter(application=str(application))

        qs = qs.order_by("-updated_at", "-id")
        return Response(
            {
                "results": [_payment_transaction_dict(tx, request) for tx in qs],
            }
        )


class PaymentOfflineSubmissionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        application = str(request.data.get("application") or "").strip()
        txn_id = str(request.data.get("txn_id") or "").strip()
        court_fees = str(request.data.get("court_fees") or "").strip()
        payment_date = str(request.data.get("payment_date") or "").strip()
        e_filing_number = str(request.data.get("e_filing_number") or "").strip()
        bank_receipt = request.FILES.get("bank_receipt")
        payment_type = str(request.data.get("payment_type") or "Court Fees").strip()

        if not application:
            return Response({"detail": "application is required."}, status=400)
        if not txn_id:
            return Response({"detail": "transaction id is required."}, status=400)
        if not court_fees:
            return Response({"detail": "court_fees is required."}, status=400)
        if not bank_receipt:
            return Response({"detail": "bank_receipt is required."}, status=400)
        if not payment_date:
            return Response({"detail": "payment_date is required."}, status=400)

        ext = os.path.splitext(str(getattr(bank_receipt, "name", "")))[1].lower()
        if ext != ".pdf":
            return Response({"detail": "bank_receipt must be a PDF file."}, status=400)

        parsed_payment_date = None
        try:
            parsed_payment_date = datetime.date.fromisoformat(payment_date)
        except Exception:
            return Response(
                {"detail": "payment_date must be in YYYY-MM-DD format."},
                status=400,
            )

        folder_key = e_filing_number or application
        folder_key = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in folder_key)
        folder_key = folder_key.strip("_") or "unknown"
        receipt_name = f"{uuid.uuid4().hex}.pdf"
        saved_path = default_storage.save(
            f"payment/bank_receipts/{folder_key}/{receipt_name}",
            bank_receipt,
        )

        payment_status = getattr(
            settings,
            "PG_PAYMENT_STATUS",
            {"initiated": "initiated", "success": "success", "failed": "failed"},
        )
        paid_status = payment_status.get("success", "success")
        reference_no = generate_payment_reference_no()

        source_offline = str(request.data.get("source") or "").strip()
        raw_ef_doc = request.data.get("efiling_document_id")
        offline_callback: dict = {
            "application": application,
            "e_filing_number": e_filing_number,
        }
        if source_offline:
            offline_callback["source"] = source_offline
        if raw_ef_doc not in (None, ""):
            try:
                offline_callback["efiling_document_id"] = int(raw_ef_doc)
            except (TypeError, ValueError):
                pass

        tx = PaymentTransaction.objects.create(
            payment_type=payment_type,
            payment_mode="offline",
            application=application,
            reference_no=reference_no,
            txn_id=txn_id,
            amount=court_fees,
            court_fees=court_fees,
            payment_date=parsed_payment_date,
            status=paid_status,
            message="Offline court fee payment recorded.",
            callback_method="OFFLINE",            
            created_by=request.user if request.user.is_authenticated else None,
            callback_payload=offline_callback,
        )
        tx.bank_receipt.name = saved_path
        tx.save(update_fields=["bank_receipt", "updated_at"])

        return Response(
            {
                "id": tx.id,
                "application": tx.application,
                "payment_mode": tx.payment_mode,
                "reference_no": tx.reference_no,
                "txn_id": tx.txn_id,
                "court_fees": tx.court_fees,
                "payment_date": (
                    tx.payment_date.isoformat() if tx.payment_date else None
                ),
                "status": tx.status,
                "bank_receipt": (
                    request.build_absolute_uri(tx.bank_receipt.url)
                    if tx.bank_receipt
                    else None
                ),
            },
            status=201,
        )


class PaymentResponseCallbackView(APIView):
    """
    Callback endpoint configured as PG return_url.
    Receives PG response and redirects to frontend status page.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        payload = self._normalise_payload(dict(request.query_params))
        return self._handle_response(payload, callback_method="GET")

    def post(self, request):
        payload = self._normalise_payload(request.data if isinstance(request.data, dict) else {})
        return self._handle_response(payload, callback_method="POST")

    def _normalise_payload(self, payload):
        normalised = {}
        for key, value in payload.items():
            if isinstance(value, list):
                normalised[key] = value[0] if value else None
            else:
                normalised[key] = value
        return normalised

    def _handle_response(self, payload, callback_method):
        pg_params = settings.PG_PARAMS
        payment_status = getattr(
            settings,
            "PG_PAYMENT_STATUS",
            {"initiated": "initiated", "success": "success", "failed": "failed"},
        )

        encdata = payload.get("encdata")
        if encdata:
            payload = self._restructure_data_from_encdata(encdata)

        reference_no = payload.get("merchant_ref_no") or payload.get("reference_no")
        tx = PaymentTransaction.objects.filter(reference_no=reference_no).first()

        if tx and not self._verify_response_checksum(payload):
            tx.status = payment_status.get("failed", "failed")
            tx.message = "Checksum verification failed."
            tx.callback_method = callback_method
            tx.callback_payload = _merge_payment_callback_payload(tx.callback_payload, payload)
            tx.save(update_fields=["status", "message", "callback_method", "callback_payload", "updated_at"])
            return HttpResponseRedirect(self._build_redirect_url(tx, "failed", "Checksum verification failed."))

        if tx:
            gateway_status = str(payload.get("status", "")).strip()
            is_success = gateway_status.lower() == "success"
            app_status = payment_status.get("success", "success") if is_success else payment_status.get("failed", "failed")
            tx.status = app_status
            tx.message = payload.get("status_desc") or payload.get("message") or app_status
            tx.amount = str(payload.get("amount") or tx.amount or "")
            tx.txn_id = payload.get("sbs_ref_no") or payload.get("txn_id")
            tx.callback_method = callback_method
            tx.callback_payload = _merge_payment_callback_payload(tx.callback_payload, payload)
            tx.save()
            return HttpResponseRedirect(self._build_redirect_url(tx, "success" if is_success else "failed", tx.message))

        # Unknown reference: fallback to new filing redirect
        base_redirect_url = pg_params.get("redirect_to_front_end_for_application_fee_paymet_status_page", "")
        separator = "&" if "?" in base_redirect_url else "?"
        return HttpResponseRedirect(f"{base_redirect_url}{separator}{urlencode({'status': 'failed'})}")

    def _build_redirect_url(self, tx: PaymentTransaction, status: str, message: str | None):
        pg_params = settings.PG_PARAMS
        payment_type = str(tx.payment_type or "").lower()
        meta = tx.callback_payload if isinstance(tx.callback_payload, dict) else {}
        source = str(meta.get("source", "new_filing")).lower()
        application_ref = str(tx.application or "").upper()
        is_ia_fee = source == "ia_filing" or application_ref.startswith("IA-FEE-")

        if is_ia_fee:
            base_redirect_url = pg_params.get(
                "redirect_to_front_end_for_ia_court_fee",
                pg_params.get("redirect_to_front_end_for_application_fee_paymet_status_page", ""),
            )
        elif source == "document_filing":
            base_redirect_url = pg_params.get(
                "redirect_to_front_end_for_document_filing",
                pg_params.get("redirect_to_front_end_for_application_fee_paymet_status_page", ""),
            )
        elif payment_type == "intimation":
            base_redirect_url = pg_params.get("redirect_to_front_end_for_intimation_fee_paymet_status_page", "")
        else:
            base_redirect_url = pg_params.get("redirect_to_front_end_for_application_fee_paymet_status_page", "")
            if source == "draft":
                base_redirect_url = pg_params.get(
                    "redirect_to_front_end_for_application_fee_paymet_status_page_draft",
                    base_redirect_url,
                )

        query_data = {
            "application": tx.application or "",
            "id": tx.application or "",
            "status": status,
            "payment_status": status,
            "reference_no": tx.reference_no or "",
            "txn_id": tx.txn_id or "",
            "amount": tx.amount or "",
            "payment_datetime": (
                tx.updated_at.isoformat() if getattr(tx, "updated_at", None) else ""
            ),
            "paid_at": (
                tx.updated_at.isoformat() if getattr(tx, "updated_at", None) else ""
            ),
        }
        if message:
            query_data["message"] = message

        separator = "&" if "?" in base_redirect_url else "?"
        redirect_url = f"{base_redirect_url}{separator}{urlencode(query_data)}"
        tx.redirect_url = redirect_url
        tx.save(update_fields=["redirect_url", "updated_at"])
        return redirect_url

    def _restructure_data_from_encdata(self, encdata):
        pgway_parameter = {}
        if encdata:
            first_array = encdata.split("|")
            for element in first_array:
                second_array = element.split("=", 1)
                if len(second_array) == 2:
                    pgway_parameter[second_array[0]] = second_array[1]
        return pgway_parameter

    def _verify_response_checksum(self, data):
        pg = settings.PG_PARAMS
        required_keys = {"sbs_ref_no", "merchant_ref_no", "amount", "status", "status_desc", "checkSum"}
        if not data or not required_keys.issubset(set(data.keys())):
            return False
        base_string = (
            f"sbs_ref_no={data['sbs_ref_no']}|"
            f"merchant_ref_no={data['merchant_ref_no']}|"
            f"amount={data['amount']}|"
            f"status={data['status']}|"
            f"status_desc={data['status_desc']}|"
        )
        checksum_string = f"{base_string}salt={pg.get('salt')}"
        hash_object = hashlib.sha256()
        hash_object.update(checksum_string.encode("utf-8"))
        return hash_object.hexdigest() == data["checkSum"]

