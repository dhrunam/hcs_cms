import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import {
  FormGroup,
  FormBuilder,
  FormsModule,
  Validators,
  ReactiveFormsModule,
} from "@angular/forms";
import { ToastrService } from "ngx-toastr";

import Swal from "sweetalert2";
import { ActivatedRoute, Params, Router, RouterLink } from "@angular/router";
import { InitialInputs } from "../../new-filing/initial-inputs/initial-inputs";
import { Litigant } from "../../new-filing/litigant/litigant";
import { EFile } from "../../new-filing/e-file/e-file";
import { UploadDocuments } from "../../new-filing/upload-documents/upload-documents";
import { EfilingService } from "../../../../../../services/advocate/efiling/efiling.services";
import { getValidationErrorMessage } from "../../../../../../utils/pdf-validation";
import {
  formatPartyLine,
  getOrderedPartyNames,
} from "../../../../../../utils/petitioner-vs-respondent";
import { HttpEventType } from "@angular/common/http";
import { firstValueFrom } from "rxjs";
import { CaseTypeService } from "../../../../../../services/master/case-type.services";
import { PaymentService } from "../../../../../../services/payment/payment.service";
import { jsPDF } from "jspdf";

@Component({
  selector: "app-edit",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    InitialInputs,
    Litigant,
    EFile,
    UploadDocuments,
    RouterLink,
  ],
  templateUrl: "./edit.html",
  styleUrls: ["./edit.css"],
})
export class Edit {
  step = 1;
  filingId: number | null = null;
  eFilingNumber: string = "";
  // filingId: number = 28;
  // eFilingNumber: string = 'ASK20240000028C202600028';
  step1Saved = false;
  step2Saved = false;
  step3Saved = false;
  litigantList: any[] = [];
  sequenceNumber_litigant: number = 1;
  isUpdateMode = false;
  docList: any[] = [];
  isDeclarationChecked = false;

  isUploadingDocuments = false;
  uploadFileProgresses: number[] = [];
  uploadCompletedToken = 0;
  caseDetailsLocked = false;
  caseDetailsData: any = null;
  filingData: any = null;
  caseTypes: any[] = [];
  paymentOutcome: "success" | "failed" | null = null;
  paymentDetails:
    | {
        txnId?: string;
        paidAt?: string;
        referenceNo?: string;
        amount?: string;
        courtFees?: string;
        paymentMode?: "online" | "offline";
        bankReceipt?: string;
        paymentDate?: string;
        outcome?: "success" | "failed" | null;
      }
    | null = null;
  paymentMode: "online" | "offline" = "online";
  offlineTransactionId = "";
  offlineCourtFees = "";
  offlineBankReceipt: File | null = null;
  offlineBankReceiptName = "";
  offlinePaymentDate = "";
  isSubmittingOfflinePayment = false;
  private readonly wpCourtFeeRupees = 250;
  private readonly wpMainPetitionMandatoryIndexes = [
    "Synopsis",
    "List of Dates and Events",
    "Writ Petition",
    "Affidavit",
    "Vakalatnama",
    "Affidavit of Service",
  ];

  form!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private toastr: ToastrService,
    private eFilingService: EfilingService,
    private caseTypeService: CaseTypeService,
    private paymentService: PaymentService,
    private route: ActivatedRoute,
    private router: Router,
  ) {
    this.form = this.fb.group({
      initialInputs: this.fb.group({
        bench: ["High Court Of Sikkim", Validators.required],
        case_type: ["", Validators.required],
        petitioner_name: ["", Validators.required],
        petitioner_contact: [
          "",
          [Validators.required, Validators.pattern(/^[0-9]{10}$/)],
        ],
        e_filing_number: [this.eFilingNumber],
      }),

      litigants: this.fb.group(
        {
          id: [""],
          name: ["", Validators.required],
          gender: [""],
          age: [""],

          sequence_number: ["", Validators.required],

          is_diffentially_abled: [false],
          is_petitioner: [true],

          is_organisation: [false],
          organization: [""],

          contact: ["", [Validators.pattern(/^[0-9]{10}$/)]],
          email: ["", [Validators.email]],

          religion: [""],
          caste: [""],
          occupation: [""],

          address: ["", Validators.required],

          state_id: [""],
          district_id: [""],

          taluka: [""],
          village: [""],
        },

        {
          validators: (group) => {
            const isOrg = group.get("is_organisation")?.value;
            const org = group.get("organization")?.value;
            const age = group.get("age")?.value;
            const gender = group.get("gender")?.value;

            if (isOrg && !org) {
              return { orgRequired: true };
            }

            if (!isOrg && !age) {
              return { ageRequired: true };
            }

            if (!isOrg && !gender) {
              return { genderRequired: true };
            }

            return null;
          },
        },
      ),

      // caseDetails: this.fb.group({
      //   cause_of_action: ["", Validators.required],
      //   date_of_cause_of_action: ["", Validators.required],
      //   dispute_state: [""],
      //   dispute_district: [""],
      //   dispute_taluka: [""],

      //   act: ["", Validators.required],
      //   section: ["", Validators.required],
      // }),

      actDetails: this.fb.group({
        act: ["", Validators.required],
        section: ["", Validators.required],
      }),

      uploadFilingDoc: this.fb.group({
        document_type: [null, Validators.required],
        final_document: [[], Validators.required],
      }),
      setDeclaration: this.fb.group({
        isDeclarationChecked: [false, Validators.requiredTrue],
      }),
    });
  }

  ngOnInit() {
    this.bindLitigantSequenceAutoGeneration();
    this.caseTypeService.get_case_types().subscribe({
      next: (data) => {
        this.caseTypes = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
    this.route.queryParams.subscribe((params) => {
      const idParam =
        params["id"] ??
        params["efiling_id"] ??
        params["e_filing_id"] ??
        params["application"];
      this.filingId = Number(idParam || 0) || null;
      this.eFilingNumber = params["e_filing_number"] || this.eFilingNumber;
      this.applyPaymentReturnQueryParams(params);
      if (this.filingId) {
        this.restorePaymentOutcomeFromStorage();
        this.loadPaymentDetailsFromBackend();
      }
      if (this.filingId) {
        this.get_litigant_list_by_filing_id();
        this.loadInitialInputs();
        this.loadDocuments();
      }
    });
  }

  get isWPCCaseType(): boolean {
    const label = this.getSelectedCaseTypeLabel().trim().toUpperCase();
    return label === "WP(C)" || (label.includes("WP") && label.includes("(C)"));
  }

  get paymentFeeRupees(): number {
    return this.isWPCCaseType ? this.wpCourtFeeRupees : 0;
  }

  get effectiveDocumentType(): string | null {
    return this.isWPCCaseType ? "Main Petition" : null;
  }

  get mandatoryIndexesForCurrentCase(): string[] {
    return this.isWPCCaseType ? this.wpMainPetitionMandatoryIndexes : [];
  }

  get requiresCourtFeePayment(): boolean {
    return this.paymentFeeRupees > 0;
  }

  get isPaymentSuccessful(): boolean {
    if (!this.requiresCourtFeePayment) return true;
    return this.paymentOutcome === "success";
  }

  /** Receipt PDF is only for successful online gateway payments (not offline upload flow). */
  get canDownloadOnlinePaymentReceipt(): boolean {
    if (!this.requiresCourtFeePayment || this.paymentOutcome !== "success") {
      return false;
    }
    const mode = this.paymentDetails?.paymentMode ?? this.paymentMode;
    return mode === "online";
  }

  downloadOnlinePaymentReceiptPdf(): void {
    if (!this.canDownloadOnlinePaymentReceipt) return;
    const pd = this.paymentDetails;
    const bench = String(
      this.initialInputsForm?.get("bench")?.value || "High Court Of Sikkim",
    );
    const caseType = this.getSelectedCaseTypeLabel().trim() || "-";
    const amountStr =
      pd?.courtFees ||
      pd?.amount ||
      String(this.paymentFeeRupees);
    const eFilingNo = this.eFilingNumber || "-";
    const filingIdStr =
      this.filingId != null ? String(this.filingId) : "-";
    const txnId = pd?.txnId?.trim() || "-";
    const referenceNo = pd?.referenceNo?.trim() || "-";
    const dateTimeLabel = this.formatPaymentReceiptDateTime();

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
      ["Court fee (INR)", `Rs. ${this.paymentFeeRupees}/-`],
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

    const safeEf = (this.eFilingNumber || `filing-${this.filingId}`).replace(
      /[^\w.-]+/g,
      "_",
    );
    const safeTxn = (pd?.txnId || "receipt").replace(/[^\w.-]+/g, "_").slice(0, 48);
    doc.save(`payment-receipt-${safeEf}-${safeTxn}.pdf`);
  }

  private formatPaymentReceiptDateTime(): string {
    const pd = this.paymentDetails;
    const raw = pd?.paidAt || pd?.paymentDate;
    if (!raw || String(raw).trim() === "") return "-";
    const d = new Date(raw as string);
    if (!Number.isNaN(d.getTime())) return d.toLocaleString();
    return String(raw);
  }

  private getSelectedCaseTypeLabel(): string {
    const fromFilingData =
      this.filingData?.case_type_detail?.type_name ||
      this.filingData?.case_type_detail?.name ||
      this.filingData?.case_type?.type_name ||
      this.filingData?.case_type?.name;
    if (fromFilingData) return String(fromFilingData);
    const caseTypeVal = this.initialInputsForm?.value?.case_type;
    if (caseTypeVal && typeof caseTypeVal === "object") {
      return caseTypeVal.type_name || caseTypeVal.full_form || caseTypeVal.name || "";
    }
    if (caseTypeVal) {
      const ct = this.caseTypes?.find((c: any) => Number(c.id) === Number(caseTypeVal));
      return ct?.type_name || ct?.full_form || ct?.name || String(caseTypeVal);
    }
    return "";
  }

  private applyPaymentReturnQueryParams(params: Params) {
    const statusRaw = params["status"] ?? params["payment_status"] ?? params["txn_status"];
    if (statusRaw === undefined || statusRaw === null || statusRaw === "") return;
    const appParam = params["application"] ?? params["id"];
    if (this.filingId && appParam !== undefined && String(appParam) !== String(this.filingId)) {
      return;
    }
    const st = String(statusRaw).trim().toLowerCase();
    if (/(success|paid|complete|ok)/i.test(st)) {
      this.paymentOutcome = "success";
    } else if (/(fail|reject|declin|error|cancel)/i.test(st)) {
      this.paymentOutcome = "failed";
    } else {
      this.paymentOutcome = "failed";
    }

    const txnId = String(
      params["txn_id"] ??
        params["transaction_id"] ??
        params["sbs_ref_no"] ??
        "",
    );
    const paidAt = String(
      params["payment_datetime"] ?? params["paid_at"] ?? "",
    );
    const referenceNo = String(params["reference_no"] ?? "");
    const amount = String(params["amount"] ?? "");

    this.paymentDetails = {
      txnId: txnId || undefined,
      paidAt: paidAt || undefined,
      referenceNo: referenceNo || undefined,
      amount: amount || undefined,
      courtFees: amount || undefined,
      paymentMode: "online",
      paymentDate: undefined,
      outcome: this.paymentOutcome,
    };
    this.paymentMode = "online";

    // Always open Payment accordion after gateway return.
    this.step = 5;
    this.moveToPreviewIfPaymentComplete();

    this.persistPaymentOutcome();
    const clean: Record<string, string | number> = {};
    if (this.filingId) clean["id"] = this.filingId;
    if (this.eFilingNumber) clean["e_filing_number"] = this.eFilingNumber;
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: clean,
      replaceUrl: true,
    });
  }

  private persistPaymentOutcome() {
    if (!this.filingId || !this.paymentOutcome) return;
    try {
      sessionStorage.setItem(
        `efiling_payment_${this.filingId}`,
        JSON.stringify({
          outcome: this.paymentOutcome,
          details: this.paymentDetails,
          at: Date.now(),
        }),
      );
    } catch {
      // ignore
    }
  }

  private restorePaymentOutcomeFromStorage() {
    if (!this.filingId || this.paymentOutcome !== null) return;
    try {
      const raw = sessionStorage.getItem(`efiling_payment_${this.filingId}`);
      if (!raw) return;
      const j = JSON.parse(raw);
      if (j?.outcome === "success" || j?.outcome === "failed") {
        this.paymentOutcome = j.outcome;
        this.paymentDetails = j?.details ?? { outcome: j.outcome };
        const mode = this.paymentDetails?.paymentMode;
        if (mode === "offline" || mode === "online") {
          this.paymentMode = mode;
        }
        this.step = 5;
      }
    } catch {
      // ignore
    }
  }

  private loadPaymentDetailsFromBackend() {
    if (!this.filingId) return;
    this.paymentService.latest(this.filingId).subscribe({
      next: (tx) => {
        if (!tx || (!tx.txn_id && !tx.reference_no && !tx.status)) return;
        const statusRaw = String(tx.status || "").toLowerCase();
        const paymentMode =
          String(tx.payment_mode || "").toLowerCase() === "offline"
            ? "offline"
            : "online";
        if (
          /(success|paid|complete|ok)/i.test(statusRaw) ||
          (paymentMode === "offline" &&
            !!tx.bank_receipt &&
            /(offline_submitted|submitted|pending|success|paid|complete|ok)/i.test(
              statusRaw,
            ))
        ) {
          this.paymentOutcome = "success";
        } else if (statusRaw) {
          this.paymentOutcome = "failed";
        }
        this.paymentMode = paymentMode;
        this.offlineTransactionId = String(tx.txn_id || "");
        this.offlineCourtFees = String(tx.court_fees || tx.amount || "");
        this.offlinePaymentDate = String(tx.payment_date || "");
        this.offlineBankReceipt = null;
        this.offlineBankReceiptName = tx.bank_receipt
          ? String(tx.bank_receipt).split("/").pop() || "bank_receipt"
          : "";
        this.paymentDetails = {
          txnId: tx.txn_id || undefined,
          paidAt: tx.payment_datetime || tx.paid_at || undefined,
          referenceNo: tx.reference_no || undefined,
          amount: tx.amount || undefined,
          courtFees: tx.court_fees || tx.amount || undefined,
          paymentMode,
          bankReceipt: tx.bank_receipt || undefined,
          paymentDate: tx.payment_date || undefined,
          outcome: this.paymentOutcome,
        };
        this.moveToPreviewIfPaymentComplete();
      },
    });
  }

  get paymentDetailsForPreview() {
    if (!this.requiresCourtFeePayment) {
      return { required: false };
    }
    return {
      required: true,
      txnId: this.paymentDetails?.txnId || "",
      paidAt: this.paymentDetails?.paidAt || "",
      referenceNo: this.paymentDetails?.referenceNo || "",
      amount: this.paymentDetails?.amount || "",
      courtFees:
        this.paymentDetails?.courtFees ||
        this.paymentDetails?.amount ||
        String(this.paymentFeeRupees),
      paymentMode: this.paymentDetails?.paymentMode || this.paymentMode,
      bankReceipt: this.paymentDetails?.bankReceipt || "",
      paymentDate:
        this.paymentDetails?.paymentDate || this.offlinePaymentDate || "",
      outcome: this.paymentOutcome,
    };
  }

  onPaymentModeChange(mode: "online" | "offline") {
    this.paymentMode = mode;
    if (mode === "offline" && !this.offlineCourtFees) {
      this.offlineCourtFees = String(this.paymentFeeRupees || "");
    }
    if (mode === "offline" && !this.offlinePaymentDate) {
      this.offlinePaymentDate = new Date().toISOString().slice(0, 10);
    }
  }

  onOfflineReceiptChange(event: Event) {
    const input = event.target as HTMLInputElement | null;
    const file = input?.files?.[0] || null;
    this.offlineBankReceipt = file;
    this.offlineBankReceiptName = file?.name || "";
  }

  async submitOfflinePayment() {
    if (!this.requiresCourtFeePayment) return;
    if (!this.filingId) {
      this.toastr.error("Save the draft before offline payment.");
      return;
    }
    const txnId = String(this.offlineTransactionId || "").trim();
    const courtFees = String(this.offlineCourtFees || "").trim();
    const paymentDate = String(this.offlinePaymentDate || "").trim();
    if (!txnId || !courtFees || !paymentDate || !this.offlineBankReceipt) {
      this.toastr.error(
        "Please fill Transaction ID, Court Fees, Date of Payment and upload Bank Receipt.",
      );
      return;
    }
    if (this.isSubmittingOfflinePayment) return;
    this.isSubmittingOfflinePayment = true;
    try {
      const res = await firstValueFrom(
        this.paymentService.submitOffline({
          application: this.filingId,
          txn_id: txnId,
          court_fees: courtFees,
          payment_date: paymentDate,
          e_filing_number: this.eFilingNumber || "",
          bank_receipt: this.offlineBankReceipt,
          payment_type: "Court Fees",
        }),
      );
      this.paymentOutcome = "success";
      this.paymentDetails = {
        txnId,
        amount: courtFees,
        courtFees,
        paymentMode: "offline",
        referenceNo: res?.reference_no || "",
        bankReceipt: res?.bank_receipt || "",
        paymentDate,
        paidAt: paymentDate,
        outcome: "success",
      };
      this.persistPaymentOutcome();
      this.step = 5;
      this.toastr.success("Offline payment details uploaded successfully.");
    } catch (e) {
      console.error(e);
      this.toastr.error("Could not upload offline payment details.");
    } finally {
      this.isSubmittingOfflinePayment = false;
    }
  }

  async confirmProceedToPay() {
    if (!this.requiresCourtFeePayment) return;
    if (!this.filingId || !this.eFilingNumber) {
      this.toastr.error("Save the draft and ensure e-filing number exists before paying.");
      return;
    }
    const res = await Swal.fire({
      title: "Proceed to pay court fee?",
      html: `You will be redirected to the payment gateway to pay <strong>₹${this.paymentFeeRupees}</strong> for this filing.`,
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, proceed to pay",
      cancelButtonText: "Cancel",
    });
    if (!res.isConfirmed) return;
    this.paymentMode = "online";
    try {
      const init = await firstValueFrom(
        this.paymentService.initiate({
          amount: this.paymentFeeRupees,
          application: this.filingId,
          e_filing_number: this.eFilingNumber,
          payment_type: "application",
          source: "draft",
        }),
      );
      this.postToGateway(init.action, init.fields as Record<string, string>);
    } catch (e) {
      console.error(e);
      this.toastr.error("Could not start payment. Please try again.");
    }
  }

  private postToGateway(action: string, fields: Record<string, string>) {
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

  private moveToPreviewIfPaymentComplete() {
    if (!this.requiresCourtFeePayment || this.paymentOutcome !== "success") return;
    if (this.step === 5) {
      this.step = 6;
      this.setCaseDetailsReviewState(true);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  get_litigant_list_by_filing_id() {
    this.eFilingService
      .get_litigant_list_by_filing_id(this.filingId || 0)
      .subscribe({
        next: (data) => {
          this.litigantList = data.results;
          this.refreshLitigantSequenceNumber();
        },
      });
  }

  get_case_details_by_filing_id() {
    this.eFilingService
      .get_case_details_by_filing_id(this.filingId || 0)
      .subscribe({
        next: (data) => {
          this.caseDetailsForm.patchValue({
            cause_of_action: data.results?.[0]?.cause_of_action || "",
            date_of_cause_of_action:
              data.results?.[0]?.date_of_cause_of_action || "",
            dispute_state: data.results?.[0]?.dispute_state || "",
            dispute_district: data.results?.[0]?.dispute_district || "",
            dispute_taluka: data.results?.[0]?.dispute_taluka || "",
            act: "",
            section: "",
          });
        },
      });
  }

  get memoOfAppealUploaded(): boolean {
    const list = Array.isArray(this.docList) ? this.docList : [];
    return list.some(
      (d: any) =>
        String(d?.document_type || "")
          .trim()
          .toLowerCase() === "memo of appeal",
    );
  }

  get uploadedIndexNames(): string[] {
    const list = Array.isArray(this.docList) ? this.docList : [];
    const names: string[] = [];
    list.forEach((doc: any) => {
      const indexes = Array.isArray(doc?.document_indexes)
        ? doc.document_indexes
        : [];
      indexes.forEach((part: any) => {
        const name = String(
          part?.document_part_name ||
            part?.document_part ||
            part?.index_name ||
            part?.name ||
            "",
        ).trim();
        if (name) names.push(name);
      });
    });
    return names;
  }

  get selectedCaseTypeId(): number | null {
    const value = this.initialInputsForm?.get("case_type")?.value;
    if (!value) return null;
    if (typeof value === "object") {
      const id = Number((value as any).id || 0);
      return Number.isFinite(id) && id > 0 ? id : null;
    }
    const parsed = Number(value);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
  }

  actList: any[] = [];

  receiveActList(data: any[]) {
    this.actList = [...this.actList, ...data];
    const shouldPersistActs =
      !!this.filingId &&
      (this.step3Saved ||
        this.caseDetailsForm.disabled ||
        this.caseDetailsLocked);

    if (shouldPersistActs) {
      data.forEach((item: any) => {
        const payload = new FormData();

        payload.append("e_filing", String(this.filingId));
        payload.append("e_filing_number", this.eFilingNumber);
        payload.append("act", item.act);
        payload.append("section", item.section);

        this.eFilingService.add_case_details_act(payload).subscribe(() => {
          this.loadActList();
        });
      });
    }

    console.log("Act list in parent page", this.actList);

    const group = this.form.get("caseDetails") as FormGroup;

    group.patchValue({
      act: "",
      section: "",
    });

    group.get("act")?.markAsPristine();
    group.get("act")?.markAsUntouched();
    group.get("section")?.markAsPristine();
    group.get("section")?.markAsUntouched();
  }

  removeAct(index: number) {
    const act = this.actList[index];
    if (act?.id && this.filingId) {
      this.eFilingService.delete_case_details_act(act.id).subscribe(() => {
        this.actList = this.actList.filter((_: any, i: number) => i !== index);
      });
      return;
    }

    this.actList = this.actList.filter((_: any, i: number) => i !== index);
  }

  pdfOnlyValidator(control: any) {
    const files: File[] = control.value;

    if (!files || files.length === 0) return null;

    const invalid = files.some((file) => file.type !== "application/pdf");

    return invalid ? { invalidFileType: true } : null;
  }

  get initialInputsForm(): FormGroup {
    return this.form.get("initialInputs") as FormGroup;
  }

  get litigantsForm(): FormGroup {
    return this.form.get("litigants") as FormGroup;
  }

  get caseDetailsForm(): FormGroup {
    return this.form.get("caseDetails") as FormGroup;
  }

  getActDetailsForm(): FormGroup {
    return this.form.get("actDetails") as FormGroup;
  }

  get uploadFilingDocForm(): FormGroup {
    return this.form.get("uploadFilingDoc") as FormGroup;
  }

  get mergeFrontPage(): {
    petitionerName: string;
    respondentName: string;
    caseNo: string;
    caseType: string;
  } {
    const init = this.initialInputsForm?.value;
    const petitionerName = String(init?.petitioner_name || "").trim();
    const petitioners = getOrderedPartyNames(this.litigantList, true);
    const respondents = getOrderedPartyNames(this.litigantList, false);

    const caseType =
      this.filingData?.case_type_detail?.type_name ||
      this.filingData?.case_type_detail?.name ||
      this.filingData?.case_type?.type_name ||
      this.filingData?.case_type?.name ||
      String(init?.case_type || "").trim();

    return {
      petitionerName: formatPartyLine(petitioners, petitionerName),
      respondentName: formatPartyLine(respondents, ""),
      caseNo: this.eFilingNumber || "",
      caseType,
    };
  }

  get setDeclarationForm(): FormGroup {
    return this.form.get("setDeclaration") as FormGroup;
  }

  getCurrentForm(): FormGroup {
    if (this.step === 1) {
      return this.form.get("litigants") as FormGroup;
    }

    return this.form;
  }

  next() {
    if (this.step === 1 && !this.hasRequiredLitigants()) {
      const message = this.hasPetitionerOnly()
        ? "At least one respondent should be added."
        : "Please complete the form before continuing.";
      this.toastr.error(message, "", {
        timeOut: 3000,
        closeButton: true,
      });
      return;
    }

    if (this.step == 1 && this.litigantList.length > 0) {
      this.step = 4;
      this.setCaseDetailsReviewState(this.step === 6);
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
      return;
    }

    if (this.step === 5) {
      if (this.requiresCourtFeePayment && !this.isPaymentSuccessful) {
        this.toastr.error("Please complete court fee payment before continuing.", "", {
          timeOut: 3500,
          closeButton: true,
        });
        return;
      }
      this.step = 6;
      this.setCaseDetailsReviewState(this.step === 6);
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
      return;
    }

    if (this.step == 4 && this.docList.length > 0) {
      if (!this.hasMandatoryWpCDocuments()) {
        this.toastr.error(
          "For WP(C), upload all mandatory Main Petition indexes before proceeding.",
        );
        return;
      }
      this.step = 5;
      this.setCaseDetailsReviewState(this.step === 6);
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
      return;
    }

    const currentForm = this.getCurrentForm();
    if (currentForm.invalid) {
      currentForm.markAllAsTouched();
      return;
    }

    if (this.step < 6) {
      this.step++;
    }

    this.setCaseDetailsReviewState(this.step === 6);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  prev() {
    if (this.step === 6) {
      this.step = 5;
    } else if (this.step === 5) {
      this.step = 4;
    } else if (this.step === 4) {
      this.step = 1;
    } else if (this.step > 1) {
      this.step--;
    }

    this.setCaseDetailsReviewState(this.step === 6);
  }

  goToStep(stepNumber: number) {
    if (stepNumber === 2 || stepNumber === 3) {
      stepNumber = 1;
    }

    const maxStep = this.getMaxAllowedStep();
    if (stepNumber > maxStep) {
      this.toastr.error(
        "Please complete the current form before moving forward.",
        "",
        {
          timeOut: 3000,
          closeButton: true,
        },
      );
      return;
    }

    this.step = stepNumber;
    this.setCaseDetailsReviewState(this.step === 6);
  }

  saveStep1() {
    const form = this.form.get("initialInputs") as FormGroup;

    if (form.invalid) {
      form.markAllAsTouched();
      return;
    }

    this.eFilingService
      .post_efiling_initial_details(form.value)
      .subscribe((res: any) => {
        this.filingId = res.id;
        this.eFilingNumber = res.e_filing_number;
        this.form.get("initialInputs")?.patchValue({
          e_filing_number: this.eFilingNumber,
        });
        this.initialInputsForm.disable();
        this.step = 2;
        this.toastr.success(
          "Saved successfully. E Filing number: " + this.eFilingNumber,
          "",
          {
            timeOut: 11000,
            closeButton: true,
            progressBar: true,
            positionClass: "toast-bottom-right",
          },
        );
      });
  }

  // saveStep2() {
  //   const form = this.form.get('litigants') as FormGroup;

  //   if (form.invalid) {
  //     form.markAllAsTouched();
  //     return;
  //   }

  //   const payload = {
  //     ...form.value,
  //     e_filing: this.filingId,
  //     e_filing_number: this.eFilingNumber,
  //   };

  //   this.eFilingService.post_litigant_details(payload).subscribe((res: any) => {
  //     this.step = 3;
  //     this.step2Saved = true;

  //     this.toastr.success('Litigant Details saved successfully', '', {
  //       timeOut: 5000,
  //       closeButton: true,
  //       progressBar: true,
  //       positionClass: 'toast-bottom-right',
  //     });
  //   });
  // }

  saveStep2() {
    const form = this.form.get("litigants") as FormGroup;
    const formValue = { ...form.getRawValue() };
    const currentLitigantId = Number(formValue.id || 0);

    if (
      !this.isSequenceNumberUnique(
        formValue.sequence_number,
        formValue.is_petitioner,
        currentLitigantId,
      )
    ) {
      const typeLabel = this.getLitigantTypeLabel(formValue.is_petitioner);
      this.toastr.error(
        `Sequence number must be unique for ${typeLabel}.`,
        "",
        {
          timeOut: 3000,
        },
      );
      form.get("sequence_number")?.markAsTouched();
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    if (formValue.is_organisation) {
      formValue.age = 0;
    }

    if (form.invalid) {
      form.markAllAsTouched();
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    const payload = {
      ...formValue,
      e_filing: this.filingId,
      e_filing_number: this.eFilingNumber,
    };

    this.eFilingService.post_litigant_details(payload).subscribe((res: any) => {
      this.litigantList.push(res);

      console.log("Litigant details are", res);

      const nextSequence = this.getNextSequenceNumber(formValue.is_petitioner);

      form.reset({
        is_diffentially_abled: false,
        is_petitioner: formValue.is_petitioner,
        sequence_number: nextSequence,
        gender: "",
        organization: "",
      });

      window.scrollTo({ top: 0, behavior: "smooth" });

      const typeLabel = this.getLitigantTypeLabel(formValue.is_petitioner);
      this.toastr.success(`1 ${typeLabel} added`, "", {
        timeOut: 3000,
      });
    });
  }

  onDelete(id: number) {
    this.litigantList = this.litigantList.filter((item) => item.id !== id);
    this.refreshLitigantSequenceNumber();
  }

  undoLitigantEdit() {
    const form = this.form.get("litigants") as FormGroup;
    form.reset({
      id: "",
      name: "",
      gender: "",
      age: "",
      sequence_number: this.getNextSequenceNumber(true),
      is_diffentially_abled: false,
      is_petitioner: true,
      is_organisation: false,
      organization: "",
      contact: "",
      email: "",
      religion: "",
      caste: "",
      occupation: "",
      address: "",
      state_id: "",
      district_id: "",
      taluka: "",
      village: "",
    });
    form.markAsPristine();
    form.markAsUntouched();
    this.refreshLitigantSequenceNumber(true);
  }

  private isSequenceNumberUnique(
    sequenceNumber: number,
    isPetitioner: boolean,
    currentLitigantId?: number,
  ): boolean {
    if (!sequenceNumber && sequenceNumber !== 0) return false;
    return !this.litigantList.some(
      (item) =>
        Number(item.id) !== Number(currentLitigantId || 0) &&
        this.normalizeIsPetitioner(item.is_petitioner) ===
          this.normalizeIsPetitioner(isPetitioner) &&
        Number(item.sequence_number) === Number(sequenceNumber),
    );
  }

  private normalizeIsPetitioner(value: any): boolean {
    return value === true || value === "true" || value === 1 || value === "1";
  }

  private getLitigantTypeLabel(isPetitioner: boolean): string {
    return this.normalizeIsPetitioner(isPetitioner)
      ? "petitioner"
      : "respondent";
  }

  private getNextSequenceNumber(isPetitioner: boolean): number {
    const maxSequence = this.litigantList
      .filter(
        (item) =>
          this.normalizeIsPetitioner(item.is_petitioner) ===
          this.normalizeIsPetitioner(isPetitioner),
      )
      .reduce(
        (max, item) => Math.max(max, Number(item.sequence_number) || 0),
        0,
      );
    return maxSequence + 1;
  }

  private refreshLitigantSequenceNumber(force = false): void {
    const form = this.litigantsForm;
    if (!form) return;
    const isEditing = Number(form.get("id")?.value || 0) > 0;
    if (isEditing && !force) return;
    const isPetitioner = this.normalizeIsPetitioner(
      form.get("is_petitioner")?.value,
    );
    form.patchValue(
      { sequence_number: this.getNextSequenceNumber(isPetitioner) },
      { emitEvent: false },
    );
  }

  private bindLitigantSequenceAutoGeneration(): void {
    const form = this.litigantsForm;
    if (!form) return;
    form.get("sequence_number")?.disable({ emitEvent: false });
    this.refreshLitigantSequenceNumber(true);
    form.get("is_petitioner")?.valueChanges.subscribe(() => {
      this.refreshLitigantSequenceNumber();
    });
  }

  private hasPetitionerOnly(): boolean {
    const hasPetitioner = this.litigantList.some((item) => item.is_petitioner);
    const hasRespondent = this.litigantList.some((item) => !item.is_petitioner);
    return hasPetitioner && !hasRespondent;
  }

  updateStep2() {
    const form = this.form.get("litigants") as FormGroup;
    const formValue = { ...form.getRawValue() };
    const litigantId = Number(formValue.id || 0);

    if (!litigantId) {
      this.toastr.error("Please select a litigant to update.");
      return;
    }

    if (
      !this.isSequenceNumberUnique(
        formValue.sequence_number,
        formValue.is_petitioner,
        litigantId,
      )
    ) {
      const typeLabel = this.getLitigantTypeLabel(formValue.is_petitioner);
      this.toastr.error(
        `Sequence number must be unique for ${typeLabel}.`,
        "",
        {
          timeOut: 3000,
        },
      );
      form.get("sequence_number")?.markAsTouched();
      return;
    }

    if (formValue.is_organisation) {
      formValue.age = 0;
    }

    if (form.invalid) {
      form.markAllAsTouched();
      return;
    }

    const payload = new FormData();
    payload.append("id", String(litigantId));
    payload.append("e_filing", String(this.filingId || ""));
    payload.append("e_filing_number", String(this.eFilingNumber || ""));
    payload.append("name", String(formValue.name || ""));
    payload.append("gender", String(formValue.gender || ""));
    payload.append("age", String(formValue.age ?? ""));
    payload.append("sequence_number", String(formValue.sequence_number ?? ""));
    payload.append(
      "is_diffentially_abled",
      String(!!formValue.is_diffentially_abled),
    );
    payload.append("is_petitioner", String(!!formValue.is_petitioner));
    payload.append("is_organisation", String(!!formValue.is_organisation));
    payload.append("organization", String(formValue.organization ?? ""));
    payload.append("contact", String(formValue.contact || ""));
    payload.append("email", String(formValue.email || ""));
    payload.append("religion", String(formValue.religion || ""));
    payload.append("caste", String(formValue.caste || ""));
    payload.append("occupation", String(formValue.occupation || ""));
    payload.append("address", String(formValue.address || ""));
    payload.append("state_id", String(formValue.state_id || ""));
    payload.append("district_id", String(formValue.district_id || ""));
    payload.append("taluka", String(formValue.taluka || ""));
    payload.append("village", String(formValue.village || ""));

    this.eFilingService
      .update_litigant_details(payload)
      .subscribe((res: any) => {
        const index = this.litigantList.findIndex(
          (item) => Number(item.id) === litigantId,
        );

        if (index > -1) {
          this.litigantList[index] = res;
        }

        form.reset({
          id: "",
          is_diffentially_abled: false,
          is_petitioner: formValue.is_petitioner,
          sequence_number: "",
          gender: "",
          organization: "",
        });

        this.toastr.success("Litigant updated successfully", "", {
          timeOut: 3000,
        });
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
  }

  saveStep3() {
    const form = this.caseDetailsForm;

    form.markAllAsTouched();

    const missingRequiredActs = this.actList.length === 0;
    const missingRequiredDetails =
      form.get("cause_of_action")?.invalid ||
      form.get("date_of_cause_of_action")?.invalid;

    if (missingRequiredActs || missingRequiredDetails) {
      this.toastr.error(
        "Please add at least one act and complete required fields.",
        "",
        {
          timeOut: 3000,
        },
      );
      if (missingRequiredDetails) {
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
      return;
    }

    const acts = this.actList.length
      ? this.actList
      : [{ act: form.value.act, section: form.value.section }];

    const payload = {
      ...form.value,
      e_filing: this.filingId,
      e_filing_number: this.eFilingNumber,
      efiling_acts: acts.map((a) => ({
        ...a,
        e_filing: this.filingId,
        e_filing_number: this.eFilingNumber,
      })),
    };

    this.eFilingService.post_case_details(payload).subscribe(() => {
      this.step3Saved = true;
      this.caseDetailsLocked = true;
      this.caseDetailsForm.disable({ emitEvent: false });
      this.caseDetailsForm.get("act")?.enable({ emitEvent: false });
      this.caseDetailsForm.get("section")?.enable({ emitEvent: false });
      this.step = 4;
    });
  }

  hasRequiredLitigants(): boolean {
    const hasPetitioner = this.litigantList.some((item) => item.is_petitioner);
    const hasRespondent = this.litigantList.some((item) => !item.is_petitioner);
    return hasPetitioner && hasRespondent;
  }

  isCaseDetailsNextDisabled(): boolean {
    const form = this.caseDetailsForm;
    const hasCause = !form.get("cause_of_action")?.invalid;
    const hasDate = !form.get("date_of_cause_of_action")?.invalid;
    const hasActs = this.actList.length > 0;
    return !hasCause || !hasDate || !hasActs;
  }

  private getMaxAllowedStep(): number {
    if (!this.hasRequiredLitigants()) return 1;
    if (this.docList.length === 0) return 4;
    if (!this.hasMandatoryWpCDocuments()) return 4;
    if (this.requiresCourtFeePayment && !this.isPaymentSuccessful) return 5;
    return 6;
  }

  private hasMandatoryWpCDocuments(): boolean {
    if (!this.isWPCCaseType) return true;
    const mainPetition = this.docList.find(
      (d: any) =>
        String(d?.document_type || "")
          .trim()
          .toLowerCase() === "main petition",
    );
    if (!mainPetition) return false;

    const names = new Set(
      (mainPetition.document_indexes || [])
        .map((x: any) => String(x?.document_part_name || "").trim().toLowerCase())
        .filter(Boolean),
    );
    const requiredWithoutAnnexure = this.wpMainPetitionMandatoryIndexes
      .filter((name) => name !== "Annexure(s)*")
      .map((name) => name.trim().toLowerCase());

    const hasRequired = requiredWithoutAnnexure.every((name) =>
      names.has(name),
    );
    if (!hasRequired) return false;
    const hasAnnexure = (mainPetition.document_indexes || []).some((x: any) =>
      /^annexure a\d+$/i.test(String(x?.document_part_name || "").trim()),
    );
    return hasAnnexure;
  }

  goToPageFromPreview(step: number) {
    if (step === 2 || step === 3) {
      step = 1;
    }
    this.step = step;
    this.setCaseDetailsReviewState(this.step === 6);
  }

  private loadCaseDetails() {
    this.eFilingService
      .get_case_details_by_filing_id(this.filingId || 0)
      .subscribe({
        next: (data) => {
          console.log("Case details data is", data);
          const details = Array.isArray(data?.results)
            ? data.results[0]
            : Array.isArray(data)
              ? data[0]
              : data;
          if (!details) return;

          this.caseDetailsData = details;

          const disputeState =
            details.dispute_state_id ??
            details.dispute_state?.id ??
            details.dispute_state ??
            "";
          const disputeDistrict =
            details.dispute_district_id ??
            details.dispute_district?.id ??
            details.dispute_district ??
            "";
          const dateOfCause = details.date_of_cause_of_action
            ? String(details.date_of_cause_of_action).slice(0, 10)
            : "";

          this.caseDetailsForm.enable({ emitEvent: false });
          this.caseDetailsForm.patchValue({
            cause_of_action: details.cause_of_action || "",
            date_of_cause_of_action: dateOfCause,
            dispute_state: disputeState,
            dispute_district: disputeDistrict,
            dispute_taluka: details.dispute_taluka || "",
            act: "",
            section: "",
          });

          this.step3Saved = true;
          this.caseDetailsLocked = true;
          this.caseDetailsForm.disable({ emitEvent: false });
          this.caseDetailsForm.get("act")?.enable({ emitEvent: false });
          this.caseDetailsForm.get("section")?.enable({ emitEvent: false });
          this.setCaseDetailsReviewState(false);
        },
      });
  }

  private loadInitialInputs() {
    this.eFilingService.get_filing_by_efiling_id(this.filingId || 0).subscribe({
      next: (data) => {
        console.log("I am here", data);
        const record = Array.isArray(data?.results) ? data.results[0] : data;
        if (!record) return;

        this.filingData = record;
        console.log("Filing data is ", this.filingData);
        const resolvedCaseTypeId =
          record.case_type?.id ?? record.case_type_id ?? record.case_type ?? "";
        this.initialInputsForm.patchValue({
          bench: record.bench || "High Court Of Sikkim",
          case_type: record.case_type?.id ?? record.case_type ?? "",
          petitioner_name: record.petitioner_name || "",
          petitioner_contact: record.petitioner_contact || "",
          e_filing_number: this.eFilingNumber || record.e_filing_number,
        });
        if (!this.eFilingNumber && record.e_filing_number) {
          this.eFilingNumber = record.e_filing_number;
        }
        this.step1Saved = true;
        this.initialInputsForm.disable({ emitEvent: false });
      },
    });
  }

  private loadActList() {
    this.eFilingService.get_acts_by_filing_id(this.filingId || 0).subscribe({
      next: (data) => {
        const rows = Array.isArray(data?.results) ? data.results : [];
        this.actList = rows.map((item: any) => ({
          id: item.id,
          act: item.act,
          actname:
            item.actname ||
            item.act_name ||
            item.act?.actname ||
            item.act?.act_name ||
            item.act?.act ||
            item.act,
          section: item.section,
        }));
      },
    });
  }

  private setCaseDetailsReviewState(isReview: boolean) {
    const form = this.caseDetailsForm;
    if (!form) return;

    if (isReview || this.caseDetailsLocked) {
      form.disable({ emitEvent: false });
      form.get("act")?.enable({ emitEvent: false });
      form.get("section")?.enable({ emitEvent: false });
      return;
    }

    form.enable({ emitEvent: false });
  }

  previewDoc(doc: any) {
    if (doc.final_document) {
      window.open(doc.final_document, "_blank");
    }
  }

  deleteDoc(id: number, index: number) {
    const confirmDelete = confirm(
      "Your document will be deleted and you need to re-upload it. Continue?",
    );

    if (!confirmDelete) return;

    this.eFilingService
      .delete_case_documnets_before_final_filing(id)
      .subscribe({
        next: (res) => {
          console.log("Deleted response", res);
          this.docList.splice(index, 1);
          this.loadDocuments();
        },
      });
  }

  async handleDocUpload(data: any) {
    if (this.isUploadingDocuments) return;
    const documentType = String(data?.document_type || "").trim();
    const uploadItems = Array.isArray(data?.items) ? data.items : [];

    if (!documentType || uploadItems.length === 0 || !this.filingId) return;

    this.isUploadingDocuments = true;
    this.uploadFileProgresses = uploadItems.map(() => 0);

    try {
      let documentRes = this.findExistingDocumentByType(documentType);
      let documentId = documentRes?.id;

      if (!documentId) {
        const documentPayload = new FormData();
        documentPayload.append("document_type", documentType);
        documentPayload.append("e_filing", String(this.filingId));
        documentPayload.append("e_filing_number", this.eFilingNumber);

        documentRes = await firstValueFrom(
          this.eFilingService.upload_case_documnets(documentPayload),
        );
        documentId = documentRes?.id;
        if (!documentId) return;
      }

      const uploadedDocumentParts: any[] = [];

      const existingIndexes = Array.isArray(documentRes?.document_indexes)
        ? documentRes.document_indexes
        : [];

      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];

        const indexPayload = new FormData();
        indexPayload.append("document", String(documentId));
        indexPayload.append(
          "document_part_name",
          String(item.index_name || "").trim(),
        );
        indexPayload.append("file_part_path", item.file);
        indexPayload.append(
          "document_sequence",
          String(existingIndexes.length + i + 1),
        );
        if (item.index_id) {
          indexPayload.append("index", String(item.index_id));
        }

        const indexRes = await this.uploadIndexFileWithProgress(
          indexPayload,
          i,
        );
        uploadedDocumentParts.push(indexRes);
      }

      const mergedIndexes = [...existingIndexes, ...uploadedDocumentParts];
      const mergedDoc = {
        ...documentRes,
        document_type: documentType,
        document_indexes: mergedIndexes,
        final_document:
          mergedIndexes[0]?.file_url || documentRes?.final_document,
      };

      const existingIndex = this.docList.findIndex(
        (doc: any) => Number(doc?.id) === Number(documentId),
      );
      if (existingIndex > -1) {
        this.docList[existingIndex] = mergedDoc;
      } else {
        this.docList.push(mergedDoc);
      }

      this.uploadCompletedToken++;
      this.loadDocuments();
    } catch (error) {
      console.error("Document upload failed", error);
      this.toastr.error(
        getValidationErrorMessage(error) ||
          "Failed to upload documents. Please try again.",
      );
    } finally {
      this.isUploadingDocuments = false;
    }
  }

  private normalizeDocType(value: any): string {
    return String(value || "")
      .trim()
      .toLowerCase();
  }

  private findExistingDocumentByType(documentType: string): any | null {
    const target = this.normalizeDocType(documentType);
    const list = Array.isArray(this.docList) ? this.docList : [];
    return (
      list.find(
        (doc: any) => this.normalizeDocType(doc?.document_type) === target,
      ) || null
    );
  }

  private loadDocuments() {
    if (!this.filingId) return;

    this.eFilingService
      .get_document_reviews_by_filing_id(this.filingId)
      .subscribe({
        next: (data) => {
          const rows = Array.isArray(data?.results) ? data.results : [];
          const grouped = new Map<string, any>();

          rows.forEach((item: any) => {
            const type = String(item?.document_type || "").trim() || "Document";
            const existing = grouped.get(type);
            const documentId =
              item?.document ||
              item?.document_id ||
              item?.documentId ||
              item?.id;

            if (existing) {
              existing.document_indexes.push(item);
              if (!existing.id && documentId) {
                existing.id = documentId;
              }
            } else {
              grouped.set(type, {
                id: documentId || null,
                document_type: type,
                document_indexes: [item],
              });
            }
          });

          this.docList = Array.from(grouped.values()).map((doc) => {
            const sortedIndexes = Array.isArray(doc.document_indexes)
              ? [...doc.document_indexes].sort((a: any, b: any) => {
                  const left = Number(a?.document_sequence) || 0;
                  const right = Number(b?.document_sequence) || 0;
                  return left - right;
                })
              : [];

            return {
              ...doc,
              document_indexes: sortedIndexes,
            };
          });
        },
      });
  }

  private uploadIndexFileWithProgress(
    formData: FormData,
    index: number,
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      this.eFilingService.upload_case_documnets_index(formData).subscribe({
        next: (event: any) => {
          if (event.type === HttpEventType.UploadProgress) {
            const total = event.total || 0;
            if (total > 0) {
              this.uploadFileProgresses[index] = Math.round(
                (event.loaded / total) * 100,
              );
            }
          }

          if (event.type === HttpEventType.Response) {
            this.uploadFileProgresses[index] = 100;
            resolve(event.body);
          }
        },
        error: (err) => reject(err),
      });
    });
  }

  saveStep4() {
    const files = this.form.get("uploadFilingDoc.documents")?.value;

    if (!files || files.length === 0) return;

    const formData = new FormData();

    files.forEach((file: File, index: number) => {
      formData.append("documents", file); // same key for multiple
    });
  }

  submit() {
    if (!this.hasMandatoryWpCDocuments()) {
      this.toastr.error(
        "For WP(C), upload all mandatory Main Petition indexes before final submission.",
      );
      this.step = 4;
      return;
    }
    Swal.fire({
      title: "Submit Filing?",
      text: "Once submitted, it will be forwarded for scrutiny.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, Submit",
      cancelButtonText: "Cancel",
    }).then((result) => {
      if (result.isConfirmed) {
        this.toastr.success("OTP has been sent successfully.", "", {
          timeOut: 3000,
          closeButton: true,
        });

        this.promptOtpAndSubmit();
      }
    });
  }

  private promptOtpAndSubmit() {
    if (!this.filingId) return;

    let submitting = false;

    Swal.fire({
      title: "Enter OTP",
      html:
        '<div style="display:flex;gap:8px;justify-content:center">' +
        ["otp-1", "otp-2", "otp-3", "otp-4"]
          .map(
            (id) =>
              `<input id="${id}" type="text" inputmode="numeric" maxlength="1" style="width:48px;height:48px;text-align:center;font-size:20px;border:1px solid #d1d5db;border-radius:8px;" />`,
          )
          .join("") +
        "</div>" +
        '<div id="otp-status" style="margin-top:12px;font-size:14px;text-align:center"></div>',
      showCancelButton: true,
      showConfirmButton: false,
      allowOutsideClick: false,
      didOpen: () => {
        const ids = ["otp-1", "otp-2", "otp-3", "otp-4"];
        const inputs = ids
          .map((id) => document.getElementById(id) as HTMLInputElement | null)
          .filter((el): el is HTMLInputElement => !!el);
        const statusEl = document.getElementById("otp-status");

        const setStatus = (message: string, color: string) => {
          if (!statusEl) return;
          statusEl.textContent = message;
          statusEl.style.color = color;
        };

        const getOtp = () => inputs.map((el) => el.value || "").join("");

        const validateOtp = () => {
          const otp = getOtp();
          if (otp.length < 4) {
            setStatus("", "");
            return;
          }

          if (otp !== "0000") {
            setStatus("OTP error. Please try again.", "#dc2626");
            return;
          }

          setStatus("OTP verified.", "#16a34a");
          if (submitting) return;
          submitting = true;

          this.eFilingService
            .final_submit_efiling(this.filingId || 0)
            .subscribe({
              next: () => {
                Swal.fire({
                  icon: "success",
                  title: "Filed Successfully",
                  text: "Your filing has been submitted for scrutiny.",
                }).then(() => {
                  this.router.navigate([
                    "/advocate/dashboard/efiling/pending-scrutiny",
                  ]);
                });
              },
              error: (err) => {
                submitting = false;
                setStatus("Submission failed. Please try again.", "#dc2626");
                console.error(err);
              },
            });
        };

        inputs.forEach((input, index) => {
          input.addEventListener("input", () => {
            input.value = input.value.replace(/\D/g, "").slice(0, 1);
            if (input.value && inputs[index + 1]) inputs[index + 1].focus();
            validateOtp();
          });

          input.addEventListener("keydown", (event) => {
            if (
              event.key === "Backspace" &&
              !input.value &&
              inputs[index - 1]
            ) {
              inputs[index - 1].focus();
            }
          });
        });

        inputs[0]?.focus();
      },
    });
  }
}
