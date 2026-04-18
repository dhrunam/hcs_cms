from django.conf import settings
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import EfilingDocuments
from apps.efiling.review_utils import submit_document_filing_for_scrutiny
from apps.payment.models import PaymentTransaction


class EfilingDocumentSubmitFilingView(APIView):
    """
    After an advocate uploads a document and pays the court fee (document_filing
    flow), this endpoint verifies a successful payment tied to the EfilingDocuments pk.
    """

    def post(self, request, pk):
        _ = request
        doc = (
            EfilingDocuments.objects.select_related("e_filing")
            .filter(pk=pk)
            .first()
        )
        if doc is None:
            return Response(
                {
                    "detail": (
                        "No document exists for this id. Upload the document again "
                        "on File Documents, pay the court fee, then submit."
                    ),
                },
                status=404,
            )
        efiling = doc.e_filing
        if not efiling:
            return Response({"detail": "E-filing not found."}, status=404)

        if doc.document_filing_submitted_at is not None:
            return Response(
                {
                    "detail": "Document filing submitted.",
                    "document_id": int(pk),
                    "e_filing_id": efiling.id,
                }
            )

        payment_status = getattr(
            settings,
            "PG_PAYMENT_STATUS",
            {"initiated": "initiated", "success": "success", "failed": "failed"},
        )
        success_label = payment_status.get("success", "success")

        qs = PaymentTransaction.objects.filter(
            application=str(efiling.id),
            status=success_label,
        ).order_by("-updated_at", "-id")

        for tx in qs:
            payload = tx.callback_payload or {}
            src = str(payload.get("source", "")).lower()
            if src not in ("document_filing", "ia_filing"):
                continue
            raw_id = payload.get("efiling_document_id")
            if raw_id is None:
                continue
            try:
                if int(raw_id) == int(pk):
                    user = (
                        request.user if getattr(request, "user", None) and request.user.is_authenticated else None
                    )
                    with transaction.atomic():
                        locked = (
                            EfilingDocuments.objects.select_for_update()
                            .select_related("e_filing")
                            .filter(pk=pk)
                            .first()
                        )
                        if locked is None:
                            return Response(
                                {
                                    "detail": (
                                        "No document exists for this id. Upload the document again "
                                        "on File Documents, pay the court fee, then submit."
                                    ),
                                },
                                status=404,
                            )
                        if locked.document_filing_submitted_at is not None:
                            return Response(
                                {
                                    "detail": "Document filing submitted.",
                                    "document_id": int(pk),
                                    "e_filing_id": locked.e_filing_id,
                                }
                            )
                        submit_document_filing_for_scrutiny(locked, user=user)
                    return Response(
                        {
                            "detail": "Document filing submitted.",
                            "document_id": int(pk),
                            "e_filing_id": efiling.id,
                        }
                    )
            except (TypeError, ValueError):
                continue

        return Response(
            {
                "detail": "No successful court fee payment found for this document. Pay the court fee first.",
            },
            status=400,
        )
