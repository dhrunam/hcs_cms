import { jsPDF } from "jspdf";

export interface OnlineCourtFeeReceiptPdfOpts {
  courtLabel?: string;
  caseTypeLabel?: string;
  eFilingNumber: string;
  amountStr: string;
  courtFeesStr?: string;
  txnId: string;
  referenceNo: string;
  paidAtIso?: string;
  paymentDate?: string;
}

function formatReceiptDateTime(paidAtIso?: string, paymentDate?: string): string {
  const raw = paidAtIso || paymentDate;
  if (!raw || String(raw).trim() === "") {
    return "-";
  }
  const d = new Date(raw as string);
  if (!Number.isNaN(d.getTime())) {
    return d.toLocaleString();
  }
  return String(raw);
}

/** Client-side PDF for a successful online court fee payment (same layout as new-filing). */
export function downloadOnlineCourtFeeReceiptPdf(
  opts: OnlineCourtFeeReceiptPdfOpts,
): void {
  const bench = String(opts.courtLabel || "High Court Of Sikkim").trim();
  const caseType = String(opts.caseTypeLabel || "-").trim() || "-";
  const amountStr = opts.amountStr;
  const courtFeesStr = opts.courtFeesStr || amountStr;
  const eFilingNo = opts.eFilingNumber || "-";
  const txnId = String(opts.txnId || "").trim() || "-";
  const referenceNo = String(opts.referenceNo || "").trim() || "-";
  const dateTimeLabel = formatReceiptDateTime(opts.paidAtIso, opts.paymentDate);

  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 14;
  let y = 18;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text("Court fee payment receipt", margin, y);
  y += 9;
  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.text(bench, margin, y);
  y += 11;

  const rows: [string, string][] = [
    ["E-filing number", eFilingNo],
    ["Case type", caseType],
    ["Payment purpose", "Court fee (e-filing)"],
    ["Transaction ID", txnId],
    ["Reference number", referenceNo],
    ["Amount paid (INR)", `Rs. ${amountStr}/-`],
    ["Court fee (INR)", `Rs. ${courtFeesStr}/-`],
    ["Payment mode", "Online"],
    ["Payment date / time", dateTimeLabel],
    ["Payment status", "Successful"],
  ];

  doc.setFontSize(10);
  const labelX = margin;
  const valueX = margin + 52;
  const valueMaxW = pageWidth - valueX - margin;

  for (const [label, value] of rows) {
    doc.setFont("helvetica", "bold");
    doc.text(`${label}:`, labelX, y);
    doc.setFont("helvetica", "normal");
    const lines = doc.splitTextToSize(String(value), valueMaxW);
    doc.text(lines, valueX, y);
    y += Math.max(6, lines.length * 5.5) + 2;
  }

  y += 6;
  doc.setFontSize(9);
  doc.setTextColor(90);
  const footer = `Generated on ${new Date().toLocaleString()}. This document is a record of your online court fee payment.`;
  doc.text(doc.splitTextToSize(footer, pageWidth - margin * 2), margin, y);
  doc.setTextColor(0);

  const safeEf = (opts.eFilingNumber || "receipt").replace(/[^\w.-]+/g, "_");
  const safeTxn = (txnId || "receipt").replace(/[^\w.-]+/g, "_").slice(0, 48);
  doc.save(`payment-receipt-${safeEf}-${safeTxn}.pdf`);
}
