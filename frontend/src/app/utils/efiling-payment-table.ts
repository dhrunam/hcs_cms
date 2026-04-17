import type { PaymentLatestResponse } from "../services/payment/payment.service";

export interface EfilingPaymentTableRow {
  id: number;
  paymentMode: "online" | "offline";
  status: string;
  txnId: string;
  referenceNo: string;
  amount: string;
  courtFees: string;
  paidAt?: string;
  paymentDate?: string;
  bankReceipt?: string | null;
  paymentType?: string;
  isSuccessful: boolean;
}

export function mapPaymentListToTableRows(
  results: PaymentLatestResponse[] | undefined | null,
): EfilingPaymentTableRow[] {
  if (!Array.isArray(results) || results.length === 0) {
    return [];
  }
  return results.map((tx) => {
    const paymentMode =
      String(tx.payment_mode || "").toLowerCase() === "offline"
        ? "offline"
        : "online";
    const statusRaw = String(tx.status || "").toLowerCase();
    let isSuccessful = false;
    if (
      /(success|paid|complete|ok)/i.test(statusRaw) ||
      (paymentMode === "offline" &&
        !!tx.bank_receipt &&
        /(offline_submitted|submitted|pending|success|paid|complete|ok)/i.test(
          statusRaw,
        ))
    ) {
      isSuccessful = true;
    }
    return {
      id: tx.id ?? 0,
      paymentMode,
      status: tx.status || "-",
      txnId: (tx.txn_id && String(tx.txn_id)) || "-",
      referenceNo: (tx.reference_no && String(tx.reference_no)) || "-",
      amount: String(tx.amount || tx.court_fees || "-"),
      courtFees: String(tx.court_fees || tx.amount || ""),
      paidAt: tx.payment_datetime || tx.paid_at,
      paymentDate: tx.payment_date,
      bankReceipt: tx.bank_receipt,
      paymentType: tx.payment_type,
      isSuccessful,
    };
  });
}

/** Show Download receipt when online+successful (PDF) or offline+successful+file URL. */
export function paymentRowHasReceiptAction(row: EfilingPaymentTableRow): boolean {
  if (!row.isSuccessful) {
    return false;
  }
  if (row.paymentMode === "offline") {
    return !!row.bankReceipt;
  }
  return row.paymentMode === "online";
}

/** Bootstrap badge class for payment status column. */
export function paymentStatusBadgeClass(row: EfilingPaymentTableRow): string {
  const s = String(row.status || "").toLowerCase();
  if (row.isSuccessful || /success|paid|complete|ok/.test(s)) {
    return "text-bg-success";
  }
  if (/fail|reject|error|declin|cancel/.test(s)) {
    return "text-bg-danger";
  }
  return "text-bg-secondary";
}
