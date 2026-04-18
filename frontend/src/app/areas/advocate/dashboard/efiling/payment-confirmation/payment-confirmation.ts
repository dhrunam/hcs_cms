import { CommonModule } from "@angular/common";
import { Component, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ActivatedRoute, Router, RouterLink } from "@angular/router";
import { firstValueFrom } from "rxjs";
import Swal from "sweetalert2";
import { ToastrService } from "ngx-toastr";
import { EfilingService } from "../../../../../services/advocate/efiling/efiling.services";
import { PaymentService } from "../../../../../services/payment/payment.service";

@Component({
  selector: "app-payment-confirmation",
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: "./payment-confirmation.html",
  styleUrls: ["./payment-confirmation.css"],
})
export class PaymentConfirmation implements OnInit {
  filingId: number | null = null;
  filing: any = null;
  paymentOutcome: "success" | "failed" | null = null;
  paymentDetails: any = null;
  isLoading = true;
  isResolving = false;
  objectionResolvedByPayment: any | null = null;
  hasPaymentObjection = false;
  paymentObjectionAmount: number | null = null;

  paymentMode: "online" | "offline" = "online";
  offlineTransactionId = "";
  offlinePaymentDate = "";
  offlineBankReceipt: File | null = null;
  offlineBankReceiptName = "";
  isSubmittingOfflinePayment = false;
  isPayingOnline = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private efilingService: EfilingService,
    private paymentService: PaymentService,
    private toastr: ToastrService,
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(async (params) => {
      this.filingId = Number(params["id"] || params["application"] || 0) || null;
      this.paymentOutcome = null;
      this.paymentDetails = null;
      this.resetPaymentForm();

      // Handle payment gateway return status (success/failed)
      const statusRaw = params["status"] ?? params["payment_status"] ?? params["txn_status"];
      if (statusRaw !== undefined && statusRaw !== null && statusRaw !== "") {
        const st = String(statusRaw).trim().toLowerCase();
        if (/(success|paid|complete|ok)/i.test(st)) {
          this.paymentOutcome = "success";
        } else if (/(fail|reject|declin|error|cancel)/i.test(st)) {
          this.paymentOutcome = "failed";
        }
      }

      if (this.filingId) {
        await this.loadFilingDetails();
      }
      this.isLoading = false;
    });
  }

  private resetPaymentForm(): void {
    this.paymentMode = "online";
    this.offlineTransactionId = "";
    this.offlinePaymentDate = "";
    this.offlineBankReceipt = null;
    this.offlineBankReceiptName = "";
  }

  private async loadFilingDetails(): Promise<void> {
    if (!this.filingId) return;

    try {
      const filing = await firstValueFrom(
        this.efilingService.get_filing_by_id(this.filingId)
      );
      this.filing = filing;
      this.objectionResolvedByPayment = filing?.objection_resolved_by_payment ?? null;
      this.hasPaymentObjection = filing?.has_payment_objection === true;
      this.paymentObjectionAmount = filing?.payment_objection_amount ?? null;

      // If objection is resolved or no active objection, load payment details to show status
      // If there's an active unresolved objection, we show the payment form regardless of past payments
      if (!this.hasPaymentObjection) {
        await this.loadPaymentDetailsFromBackend();
      }
    } catch (error) {
      console.error("Failed to load filing details", error);
      this.toastr.error("Failed to load filing details");
    }
  }

  private async loadPaymentDetailsFromBackend(): Promise<void> {
    if (!this.filingId) return;
    try {
      const tx = await firstValueFrom(this.paymentService.latest(this.filingId));
      if (tx && (tx.txn_id || tx.reference_no || tx.status)) {
        const statusRaw = String(tx.status || "").toLowerCase();
        const paymentMode =
          String(tx.payment_mode || "").toLowerCase() === "offline" ? "offline" : "online";
        if (
          /(success|paid|complete|ok)/i.test(statusRaw) ||
          (paymentMode === "offline" && !!tx.bank_receipt)
        ) {
          this.paymentOutcome = "success";
        } else if (statusRaw) {
          this.paymentOutcome = "failed";
        }
        this.paymentDetails = {
          txnId: tx.txn_id || undefined,
          paidAt: tx.payment_datetime || tx.paid_at || undefined,
          referenceNo: tx.reference_no || undefined,
          amount: tx.amount || undefined,
          courtFees: tx.court_fees || tx.amount || undefined,
          paymentMode,
          bankReceipt: tx.bank_receipt || undefined,
          paymentDate: tx.payment_date || undefined,
        };
      }
    } catch (error) {
      console.error("Failed to load payment details", error);
    }
  }

  get isObjectionResolved(): boolean {
    return this.objectionResolvedByPayment !== null && this.hasPaymentObjection === false;
  }

  get showPaymentForm(): boolean {
    // Show form if: active objection exists AND payment hasn't failed
    // If payment failed, show "Payment Failed" card instead
    return this.hasPaymentObjection && !this.isObjectionResolved && this.paymentOutcome !== 'failed';
  }

  get canSubmitOffline(): boolean {
    return (
      !!this.offlineTransactionId.trim() &&
      !!this.offlinePaymentDate &&
      !!this.offlineBankReceipt &&
      this.paymentObjectionAmount !== null &&
      this.paymentObjectionAmount > 0 &&
      !this.isSubmittingOfflinePayment
    );
  }

  onPaymentModeChange(mode: "online" | "offline"): void {
    this.paymentMode = mode;
  }

  onOfflineReceiptChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      if (file.size > 10 * 1024 * 1024) {
        this.toastr.error("File size must be less than 10MB");
        return;
      }
      this.offlineBankReceipt = file;
      this.offlineBankReceiptName = file.name;
    }
  }

  async proceedToPayOnline(): Promise<void> {
    if (!this.filingId || !this.paymentObjectionAmount || this.paymentObjectionAmount <= 0) {
      this.toastr.error("Invalid payment amount");
      return;
    }

    const result = await Swal.fire({
      title: "Proceed to pay court fee?",
      html: `You will be redirected to the payment gateway to pay <strong>₹${this.paymentObjectionAmount}</strong> for this filing.`,
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, proceed to pay",
      cancelButtonText: "Cancel",
    });
    if (!result.isConfirmed) return;

    this.isPayingOnline = true;
    try {
      const init = await firstValueFrom(
        this.paymentService.initiate({
          amount: this.paymentObjectionAmount,
          application: this.filingId,
          e_filing_number: this.filing?.e_filing_number || "",
          payment_type: "application",
          source: "objection",
        })
      );
      this.postToGateway(init.action, init.fields as Record<string, string>);
    } catch (e) {
      console.error(e);
      this.isPayingOnline = false;
      this.toastr.error("Could not start payment. Please try again.");
    }
  }

  private postToGateway(action: string, fields: Record<string, string>): void {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = action;
    form.style.display = "none";
    form.acceptCharset = "UTF-8";
    for (const [key, value] of Object.entries(fields)) {
      const inp = document.createElement("input");
      inp.type = "hidden";
      inp.name = key;
      inp.value = value == null ? "" : String(value);
      form.appendChild(inp);
    }
    document.body.appendChild(form);
    form.submit();
  }

  async submitOfflinePayment(): Promise<void> {
    if (!this.canSubmitOffline || !this.filingId) return;

    this.isSubmittingOfflinePayment = true;
    try {
      await firstValueFrom(
        this.paymentService.submitOffline({
          application: this.filingId,
          txn_id: this.offlineTransactionId.trim(),
          court_fees: this.paymentObjectionAmount!,
          payment_date: this.offlinePaymentDate,
          payment_type: "Court Fees",
          e_filing_number: this.filing?.e_filing_number || "",
          bank_receipt: this.offlineBankReceipt!,
        })
      );

      this.toastr.success("Offline payment submitted successfully!");
      await this.loadFilingDetails();
      this.resetPaymentForm();
    } catch (error: any) {
      console.error("Failed to submit offline payment", error);
      this.toastr.error(error?.error?.detail || "Failed to submit offline payment");
    } finally {
      this.isSubmittingOfflinePayment = false;
    }
  }

  async resubmitForScrutiny(): Promise<void> {
    if (!this.filingId || !this.isObjectionResolved) {
      this.toastr.error("Objection is not resolved. Please make the correct payment first.");
      return;
    }

    const result = await Swal.fire({
      title: "Resubmit for Scrutiny?",
      html: "Your filing will be resubmitted for scrutiny. The scrutiny officer will review your corrected payment.",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, Resubmit",
      cancelButtonText: "Cancel",
      confirmButtonColor: "#198754",
      cancelButtonColor: "#6c757d",
    });

    if (!result.isConfirmed) return;

    this.isResolving = true;
    try {
      const response = await firstValueFrom(
        this.efilingService.resubmit_after_payment_objection(this.filingId)
      );
      this.toastr.success("Filing resubmitted for scrutiny successfully!");
      this.router.navigate(["/advocate/dashboard/efiling/pending-scrutiny"]);
    } catch (error: any) {
      console.error("Failed to resubmit", error);
      this.toastr.error(error?.error?.error || error?.message || "Failed to resubmit filing.");
    } finally {
      this.isResolving = false;
    }
  }

  goToPendingScrutiny(): void {
    this.router.navigate(["/advocate/dashboard/efiling/pending-scrutiny"]);
  }

  formatDateTime(dateStr: string | undefined): string {
    if (!dateStr) return "-";
    const d = new Date(dateStr);
    if (!Number.isNaN(d.getTime())) return d.toLocaleString();
    return String(dateStr);
  }
}