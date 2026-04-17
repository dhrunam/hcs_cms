import { CommonModule } from "@angular/common";
import { HttpEventType } from "@angular/common/http";
import { Component, OnInit } from "@angular/core";
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import { ActivatedRoute, Params, Router, RouterLink } from "@angular/router";
import { firstValueFrom } from "rxjs";
import { forkJoin } from "rxjs";
import { ToastrService } from "ngx-toastr";
import Swal from "sweetalert2";

import { app_url } from "../../../../../../environment";
import { EfilingService } from "../../../../../../services/advocate/efiling/efiling.services";
import { PaymentService } from "../../../../../../services/payment/payment.service";
import {
  getValidationErrorMessage,
  validatePdfFiles,
  validatePdfOcrForFiles,
} from "../../../../../../utils/pdf-validation";
import {
  formatPartyLine,
  formatPetitionerVsRespondent,
  getOrderedPartyNames,
} from "../../../../../../utils/petitioner-vs-respondent";
import { UploadDocuments } from "../../new-filing/upload-documents/upload-documents";

export type ExistingCaseLitigantType =
  | "PETITIONER"
  | "RESPONDENT"
  | "APPELLANT";

export const EXISTING_CASE_LITIGANT_OPTIONS: ReadonlyArray<{
  value: ExistingCaseLitigantType;
  label: string;
}> = [
  { value: "PETITIONER", label: "Petitioner" },
  { value: "RESPONDENT", label: "Respondent" },
  { value: "APPELLANT", label: "Appellant" },
];

interface DocumentFilingUiSnapshot {
  filingId: number;
  e_filing_number: string;
  litigantType: ExistingCaseLitigantType;
  selectedIaId: number | null;
  selectedDocumentType: string;
  documentTypeSearchQuery: string;
  /** EfilingDocuments row id after upload; required for pay + submit flow. */
  pendingEfilingDocumentId?: number;
  /** Present when an online payment was started for a specific upload attempt. */
  uploadNonce?: string;
}

/** Session token: payment for a specific uploaded document (existing-case filing). */
interface DocumentUploadPaymentToken {
  eFilingId: number;
  documentType: string;
  iaId: number | null;
  efilingDocumentId: number;
  uploadNonce: string;
  referenceNo?: string;
  txnId?: string;
  amount?: string;
  paymentMode: "online" | "offline";
  paidAt: number;
}

/** Upload finished; user must pay fee then call Submit filing. */
interface PendingDocumentFilingSubmit {
  efilingDocumentId: number;
  documentType: string;
  iaId: number | null;
}

const UPLOAD_PAYMENT_TTL_MS = 45 * 60 * 1000;

@Component({
  selector: "app-document-filing-create",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
    UploadDocuments,
  ],
  templateUrl: "./create.html",
  styleUrl: "./create.css",
})
export class Create implements OnInit {
  uploadFilingDocForm!: FormGroup;
  filings: any[] = [];
  filingsWithLitigants: Array<{ filing: any; litigants: any[] }> = [];
  searchQuery = "";
  isDropdownOpen = false;
  selectedFiling: any = null;

  iaList: any[] = [];
  iaSearchQuery = "";
  iaDropdownOpen = false;
  selectedIa: any = null;

  isLoadingFilings = true;
  isLoadingCase = false;
  caseDetails: any = null;

  existingDocList: any[] = [];
  uploadedDocList: any[] = [];

  isUploadingDocuments = false;
  private isUploadRequestInFlight = false;
  isMergingPdf = false;
  mergeError: string | null = null;
  uploadFileProgresses: number[] = [];
  uploadCompletedToken = 0;

  selectedEfilingId: number | null = null;
  selectedEfilingNumber = "";
  documentTypeOptions: any[] = [];
  isDocumentTypeDropdownOpen = false;
  documentTypeSearchQuery = "";
  selectedDocumentType = "";

  litigantType: ExistingCaseLitigantType = "PETITIONER";

  /** From payment gateway query params; used until UI restore selects the filing. */
  routePaymentFilingId: number | null = null;
  private pendingDocumentFilingUiRestore = false;
  isCourtFeePaymentInProgress = false;
  isSubmitDocumentFilingInProgress = false;

  /**
   * Set after a successful document upload until Submit filing completes
   * (or user deletes that document / changes case).
   */
  pendingDocumentFilingSubmit: PendingDocumentFilingSubmit | null = null;

  constructor(
    private fb: FormBuilder,
    private eFilingService: EfilingService,
    private toastr: ToastrService,
    private paymentService: PaymentService,
    private route: ActivatedRoute,
    private router: Router,
  ) {
    this.uploadFilingDocForm = this.fb.group({
      document_type: ["", Validators.required],
      final_document: [null],
    });
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      const idParam =
        params["id"] ??
        params["application"] ??
        params["efiling_id"] ??
        params["e_filing_id"];
      this.routePaymentFilingId = Number(idParam || 0) || null;
      if (params["e_filing_number"]) {
        this.selectedEfilingNumber = String(params["e_filing_number"]);
      }
      this.applyPaymentReturnQueryParams(params);
    });
    this.loadFilings();
  }

  private get paymentTargetFilingId(): number | null {
    return this.routePaymentFilingId ?? this.selectedEfilingId;
  }

  loadFilings(): void {
    this.isLoadingFilings = true;
    this.eFilingService.get_filings().subscribe({
      next: (data: any) => {
        this.filings = data.results.filter(
          (f: any) => f?.id && f?.e_filing_number,
        );
        this.loadLitigantsForFilings();
        console.log("Filings are", this.filings);
      },
      error: () => {
        this.filings = [];
        this.isLoadingFilings = false;
        this.tryRestoreDocumentFilingUiAfterFilingsReady();
      },
    });
  }

  get_document_index_for_existing_filing(id: number) {
    this.eFilingService.get_document_index_for_existing_filing(id).subscribe({
      next: (data) => {
        this.documentTypeOptions = data.results.sort(
          (a: any, b: any) => a.sequence_number - b.sequence_number,
        );
        console.log(
          "After calling get document index by case type api",
          this.documentTypeOptions,
        );
      },
    });
  }

  private loadLitigantsForFilings(): void {
    if (this.filings.length === 0) {
      this.filingsWithLitigants = [];
      this.isLoadingFilings = false;
      this.tryRestoreDocumentFilingUiAfterFilingsReady();
      return;
    }
    const requests = this.filings.map((f) =>
      this.eFilingService.get_litigant_list_by_filing_id(Number(f.id)),
    );
    forkJoin(requests).subscribe({
      next: (litigantResults) => {
        this.filingsWithLitigants = this.filings.map((filing, i) => {
          const list = Array.isArray(litigantResults[i])
            ? litigantResults[i]
            : (litigantResults[i]?.results ?? []);
          return { filing, litigants: list };
        });
        this.isLoadingFilings = false;
        this.tryRestoreDocumentFilingUiAfterFilingsReady();
      },
      error: () => {
        this.filingsWithLitigants = this.filings.map((f) => ({
          filing: f,
          litigants: [],
        }));
        this.isLoadingFilings = false;
        this.tryRestoreDocumentFilingUiAfterFilingsReady();
      },
    });
  }

  private tryRestoreDocumentFilingUiAfterFilingsReady(): void {
    if (!this.pendingDocumentFilingUiRestore) return;
    this.pendingDocumentFilingUiRestore = false;
    this.restoreDocumentFilingUiFromStorage();
  }

  get filteredFilingsWithLitigants(): Array<{ filing: any; litigants: any[] }> {
    const q = (this.searchQuery || "").trim().toLowerCase();
    if (!q) return this.filingsWithLitigants;
    return this.filingsWithLitigants.filter((item) => {
      const ef = (item.filing.e_filing_number || "").toLowerCase();
      const ct = (item.filing.case_type?.type_name || "").toLowerCase();
      const pn = (item.filing.petitioner_name || "").toLowerCase();
      const petNames = getOrderedPartyNames(item.litigants, true)
        .join(" ")
        .toLowerCase();
      const resNames = getOrderedPartyNames(item.litigants, false)
        .join(" ")
        .toLowerCase();
      const vsLine = this.getLitigantLabel(item).toLowerCase();
      return (
        ef.includes(q) ||
        ct.includes(q) ||
        pn.includes(q) ||
        petNames.includes(q) ||
        resNames.includes(q) ||
        vsLine.includes(q)
      );
    });
  }

  getLitigantLabel(item: { filing: any; litigants: any[] }): string {
    return (
      formatPetitionerVsRespondent(
        item.litigants,
        String(item.filing?.petitioner_name || ""),
      ) || "—"
    );
  }

  /**
   * From selected filing's `case_type.annexure_type`: A → Appellant/Respondent;
   * P or default → Petitioner/Respondent. Values stay PETITIONER|RESPONDENT|APPELLANT.
   */
  get litigantTypeOptions(): ReadonlyArray<{
    value: ExistingCaseLitigantType;
    label: string;
  }> {
    if (!this.selectedFiling) {
      return EXISTING_CASE_LITIGANT_OPTIONS;
    }
    const at = String(this.selectedFiling?.case_type?.annexure_type ?? "")
      .trim()
      .toUpperCase();
    if (at === "A") {
      return [
        { value: "APPELLANT", label: "Appellant" },
        { value: "RESPONDENT", label: "Respondent" },
      ];
    }
    return [
      { value: "PETITIONER", label: "Petitioner" },
      { value: "RESPONDENT", label: "Respondent" },
    ];
  }

  litigantTypeLabel(): string {
    const row = this.litigantTypeOptions.find(
      (o) => o.value === this.litigantType,
    );
    return row?.label ?? "Petitioner";
  }

  litigantAnnexureLetter(): "P" | "A" | "R" {
    const map: Record<ExistingCaseLitigantType, "P" | "A" | "R"> = {
      PETITIONER: "P",
      APPELLANT: "A",
      RESPONDENT: "R",
    };
    return map[this.litigantType] ?? "P";
  }

  selectFiling(item: { filing: any }): void {
    console.log("Selected item for filing is", item);
    console.log(item.filing.case_type.id);

    if (this.selectedEfilingId) {
      this.clearUploadPaymentTokenForFiling(this.selectedEfilingId);
    }
    this.pendingDocumentFilingSubmit = null;

    this.get_document_index_for_existing_filing(item.filing.case_type.id);
    this.selectedFiling = item.filing;
    this.selectedEfilingId = item.filing.id;
    this.selectedEfilingNumber = String(item.filing.e_filing_number ?? "");
    this.isDropdownOpen = false;
    this.searchQuery = "";
    this.selectedIa = null;
    {
      const at = String(item.filing?.case_type?.annexure_type ?? "")
        .trim()
        .toUpperCase();
      this.litigantType = at === "A" ? "APPELLANT" : "PETITIONER";
    }
    this.uploadedDocList = [];
    this.selectedDocumentType = "";
    this.documentTypeSearchQuery = "";
    this.uploadFilingDocForm.reset();
    this.loadIasForFiling();
    this.loadSelectedCaseDetailsAndDocs();
  }

  private loadIasForFiling(onDone?: () => void): void {
    if (!this.selectedEfilingId) {
      this.iaList = [];
      onDone?.();
      return;
    }
    this.eFilingService
      .get_ias_by_efiling_id(this.selectedEfilingId)
      .subscribe({
        next: (res) => {
          const rows = Array.isArray(res) ? res : (res?.results ?? []);
          this.iaList = rows.filter((ia: any) => ia?.id);
          onDone?.();
        },
        error: () => {
          this.iaList = [];
          onDone?.();
        },
      });
  }

  get filteredIaList(): any[] {
    const q = (this.iaSearchQuery || "").trim().toLowerCase();
    if (!q) return this.iaList;
    return this.iaList.filter((ia) => {
      const iaNum = (ia?.ia_number ?? "").toLowerCase();
      const iaText = (ia?.ia_text ?? "").toLowerCase();
      const status = (ia?.status ?? "").toLowerCase();
      return iaNum.includes(q) || iaText.includes(q) || status.includes(q);
    });
  }

  selectIa(ia: any | null): void {
    if (this.pendingDocumentFilingSubmit) {
      this.toastr.warning(
        "Finish paying and submit filing for the uploaded document first, or delete that document from the list above.",
        "",
        { timeOut: 6000, closeButton: true },
      );
      return;
    }
    this.selectedIa = ia;
    this.iaDropdownOpen = false;
    this.iaSearchQuery = "";
  }

  getSelectedIaLabel(): string {
    if (!this.selectedIa) return "";
    const iaNum = this.selectedIa.ia_number || "-";
    const status = this.selectedIa.status || "Pending";
    const snippet = (this.selectedIa.ia_text || "").slice(0, 50);
    return `${iaNum} (${status})${snippet ? " - " + snippet + (this.selectedIa.ia_text?.length > 50 ? "..." : "") : ""}`;
  }

  trackIa(_: number, ia: any): number {
    return ia?.id ?? 0;
  }

  getIaStatusBadgeClass(status: string | null): string {
    const s = (status ?? "").trim().toLowerCase();
    if (s.includes("accept")) return "status-badge-success";
    if (s.includes("reject") || s.includes("partial"))
      return "status-badge-danger";
    return "status-badge-warning";
  }

  getSelectedLabel(): string {
    if (!this.selectedFiling) return "";
    const item = this.filingsWithLitigants.find(
      (x) => x.filing.id === this.selectedFiling.id,
    );
    if (!item)
      return `${this.selectedFiling.e_filing_number} | ${this.selectedFiling.case_type?.type_name || "N/A"}`;
    return `${this.selectedFiling.e_filing_number} | ${this.selectedFiling.case_type?.type_name || "N/A"} | ${this.getLitigantLabel(item)}`;
  }

  private loadSelectedCaseDetailsAndDocs(): void {
    if (!this.selectedEfilingId) return;

    this.isLoadingCase = true;
    this.caseDetails = null;
    this.existingDocList = [];

    forkJoin({
      caseDetails: this.eFilingService.get_case_details_by_filing_id(
        this.selectedEfilingId,
      ),
      documents: this.eFilingService.get_documents_by_filing_id(
        this.selectedEfilingId,
      ),
      documentIndexes: this.eFilingService.get_document_reviews_by_filing_id(
        this.selectedEfilingId,
        false,
      ),
    }).subscribe({
      next: ({ caseDetails, documents, documentIndexes }) => {
        const caseRows = caseDetails?.results ?? [];
        this.caseDetails = caseRows?.[0] ?? null;

        const mainDocs = documents?.results ?? [];
        const indexParts = documentIndexes?.results ?? [];

        this.existingDocList = mainDocs.map((doc: any) => {
          const partsForDoc = indexParts
            .filter((p: any) => Number(p.document) === Number(doc.id))
            .sort(
              (a: any, b: any) =>
                Number(a.document_sequence) - Number(b.document_sequence),
            );

          return {
            ...doc,
            document_indexes: partsForDoc,
          };
        });

        this.isLoadingCase = false;
      },
      error: () => {
        this.isLoadingCase = false;
        this.toastr.error("Failed to load case details.");
      },
    });
  }

  deleteDoc(id: number, index: number): void {
    const confirmDelete = confirm(
      "Your document will be deleted and you need to re-upload it. Continue?",
    );
    if (!confirmDelete) return;

    this.eFilingService
      .delete_case_documnets_before_final_filing(id)
      .subscribe({
        next: () => {
          this.uploadedDocList.splice(index, 1);
          if (this.pendingDocumentFilingSubmit?.efilingDocumentId === id) {
            this.pendingDocumentFilingSubmit = null;
            if (this.selectedEfilingId) {
              this.clearUploadPaymentTokenForFiling(this.selectedEfilingId);
            }
          }
          this.toastr.success("Document deleted.");
        },
        error: () => {
          this.toastr.error("Failed to delete document.");
        },
      });
  }

  trackByDocId(_: number, item: any): number {
    return item?.id ?? 0;
  }

  private maxDocumentSequence(parts: any[]): number {
    if (!Array.isArray(parts) || parts.length === 0) return 0;
    return parts.reduce(
      (m, p) => Math.max(m, Number(p?.document_sequence) || 0),
      0,
    );
  }

  getDocDisplayLabel(doc: any): string {
    if (doc?.ia_number && doc?.document_type === "IA") return doc.ia_number;
    return doc?.document_type || "-";
  }

  isWpcCaseTypeSelected(): boolean {
    const raw = String(
      this.selectedFiling?.case_type?.type_name ||
        this.selectedFiling?.case_type?.full_form ||
        "",
    )
      .trim()
      .toUpperCase();
    const normalized = raw.replace(/\s+/g, "");
    return normalized === "WP(C)";
  }

  trackFilingItem(_: number, item: { filing: any }): number {
    return item?.filing?.id ?? 0;
  }

  // get filteredDocumentTypeOptions(): string[] {
  //   const q = String(this.documentTypeSearchQuery || "")
  //     .trim()
  //     .toLowerCase();
  //   if (!q) return this.documentTypeOptions;
  //   return this.documentTypeOptions.filter((x) => x.toLowerCase().includes(q));
  // }

  selectDocumentType(option: any): void {
    if (this.pendingDocumentFilingSubmit) {
      this.toastr.warning(
        "Finish paying and submit filing for the uploaded document first, or delete that document from the list above.",
        "",
        { timeOut: 6000, closeButton: true },
      );
      return;
    }
    this.selectedDocumentType = option.name;
    this.documentTypeSearchQuery = "";
    this.isDocumentTypeDropdownOpen = false;
  }

  getSelectedDocumentTypeLabel(): string {
    return this.selectedDocumentType || "";
  }

  private isDocumentVerified(doc: any): boolean {
    const indexes = doc?.document_indexes ?? [];
    if (indexes.length === 0) return false;
    return indexes.every((p: any) => {
      const s = (p?.scrutiny_status ?? "").trim().toLowerCase();
      return s.includes("accept");
    });
  }

  get verifiedDocList(): any[] {
    return this.existingDocList.filter((doc) => this.isDocumentVerified(doc));
  }

  get nonVerifiedDocList(): any[] {
    return this.existingDocList.filter((doc) => !this.isDocumentVerified(doc));
  }

  private uploadPaymentStorageKey(eFilingId: number): string {
    return `document_filing_upload_payment_${eFilingId}`;
  }

  private generateUploadNonce(): string {
    const c = globalThis.crypto;
    if (c?.randomUUID) return c.randomUUID();
    return `${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
  }

  private escapeHtml(s: string): string {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  private saveUploadPaymentToken(t: DocumentUploadPaymentToken): void {
    try {
      sessionStorage.setItem(
        this.uploadPaymentStorageKey(t.eFilingId),
        JSON.stringify(t),
      );
    } catch {
      /* ignore */
    }
  }

  private clearUploadPaymentTokenForFiling(eFilingId: number): void {
    try {
      sessionStorage.removeItem(this.uploadPaymentStorageKey(eFilingId));
    } catch {
      /* ignore */
    }
  }

  private consumeUploadPaymentTokenAfterSuccessfulSubmit(): void {
    const id = this.selectedEfilingId;
    if (id) this.clearUploadPaymentTokenForFiling(id);
  }

  private hasValidUploadPaymentToken(
    documentType: string,
    iaId: number | null,
    efilingDocumentId: number,
  ): boolean {
    const id = this.selectedEfilingId;
    if (!id) return false;
    try {
      const raw = sessionStorage.getItem(this.uploadPaymentStorageKey(id));
      if (!raw) return false;
      const t = JSON.parse(raw) as DocumentUploadPaymentToken;
      if (Date.now() - t.paidAt > UPLOAD_PAYMENT_TTL_MS) {
        this.clearUploadPaymentTokenForFiling(id);
        return false;
      }
      if (String(t.documentType) !== String(documentType)) return false;
      const a = t.iaId == null ? null : Number(t.iaId);
      const b = iaId == null ? null : Number(iaId);
      if (a !== b) return false;
      if (Number(t.efilingDocumentId) !== Number(efilingDocumentId)) return false;
      return true;
    } catch {
      return false;
    }
  }

  private persistDocumentFilingUiSnapshotForUploadPayment(
    documentType: string,
    iaId: number | null,
    uploadNonce: string,
    pendingEfilingDocumentId: number,
  ): void {
    const filingId = this.selectedEfilingId;
    if (!filingId) return;
    try {
      const snap: DocumentFilingUiSnapshot = {
        filingId,
        e_filing_number: this.selectedEfilingNumber || "",
        litigantType: this.litigantType,
        selectedIaId: iaId,
        selectedDocumentType: documentType,
        documentTypeSearchQuery: this.documentTypeSearchQuery || "",
        pendingEfilingDocumentId,
        uploadNonce,
      };
      sessionStorage.setItem(
        `document_filing_ui_${filingId}`,
        JSON.stringify(snap),
      );
    } catch {
      /* ignore */
    }
  }

  private applyPaymentReturnQueryParams(params: Params): void {
    const statusRaw =
      params["status"] ?? params["payment_status"] ?? params["txn_status"];
    if (statusRaw === undefined || statusRaw === null || statusRaw === "") {
      return;
    }
    const appParam = params["application"] ?? params["id"];
    const currentId = this.paymentTargetFilingId;
    if (
      currentId &&
      appParam !== undefined &&
      String(appParam) !== String(currentId)
    ) {
      return;
    }
    const st = String(statusRaw).trim().toLowerCase();
    const success = /(success|paid|complete|ok)/i.test(st);

    const txnId = String(
      params["txn_id"] ??
        params["transaction_id"] ??
        params["sbs_ref_no"] ??
        "",
    );
    const referenceNo = String(params["reference_no"] ?? "");
    const amount = String(params["amount"] ?? "");

    const fid =
      (this.routePaymentFilingId ?? Number(appParam || 0)) || null;

    if (success && fid) {
      try {
        const raw = sessionStorage.getItem(`document_filing_ui_${fid}`);
        const snap = raw
          ? (JSON.parse(raw) as DocumentFilingUiSnapshot)
          : null;
        if (
          snap?.uploadNonce &&
          snap.pendingEfilingDocumentId != null
        ) {
          this.saveUploadPaymentToken({
            eFilingId: Number(fid),
            documentType: snap.selectedDocumentType || "",
            iaId: snap.selectedIaId ?? null,
            efilingDocumentId: Number(snap.pendingEfilingDocumentId),
            uploadNonce: snap.uploadNonce,
            referenceNo: referenceNo || undefined,
            txnId: txnId || undefined,
            amount: amount || undefined,
            paymentMode: "online",
            paidAt: Date.now(),
          });
          this.toastr.success(
            "Payment received. Your selections are restored. Click Submit filing to complete.",
            "",
            { timeOut: 10000, closeButton: true },
          );
        }
      } catch {
        /* ignore */
      }
    } else if (!success) {
      this.toastr.error("Payment was not successful. Please try again.");
    }

    this.pendingDocumentFilingUiRestore = true;

    let efNum = this.selectedEfilingNumber;
    if (!efNum && fid) {
      try {
        const raw = sessionStorage.getItem(`document_filing_ui_${fid}`);
        if (raw) {
          const s = JSON.parse(raw) as DocumentFilingUiSnapshot;
          efNum = s?.e_filing_number || "";
        }
      } catch {
        /* ignore */
      }
    }
    const clean: Record<string, string | number> = {};
    if (fid) clean["id"] = fid;
    if (efNum) clean["e_filing_number"] = efNum;

    this.router.navigate(
      ["/advocate/dashboard/efiling/document-filing/create"],
      { queryParams: clean, replaceUrl: true },
    );
  }

  private restoreDocumentFilingUiFromStorage(): void {
    const fid =
      this.routePaymentFilingId ?? this.selectedEfilingId;
    if (!fid) return;
    const row = this.filingsWithLitigants.find(
      (x) => Number(x.filing.id) === Number(fid),
    );
    if (!row) return;

    let snap: DocumentFilingUiSnapshot | null = null;
    try {
      const raw = sessionStorage.getItem(`document_filing_ui_${fid}`);
      if (raw) snap = JSON.parse(raw) as DocumentFilingUiSnapshot;
    } catch {
      /* ignore */
    }

    if (snap && Number(snap.filingId) === Number(fid)) {
      this.applyFilingForRestore(row.filing, snap);
    } else {
      this.applyFilingMinimalAfterPayment(row.filing);
    }
  }

  private applyFilingForRestore(
    filing: any,
    snap: DocumentFilingUiSnapshot,
  ): void {
    this.get_document_index_for_existing_filing(filing.case_type.id);
    this.selectedFiling = filing;
    this.selectedEfilingId = Number(filing.id);
    this.selectedEfilingNumber =
      snap.e_filing_number || String(filing.e_filing_number ?? "");
    this.isDropdownOpen = false;
    this.searchQuery = "";
    this.litigantType = snap.litigantType;
    this.selectedDocumentType = snap.selectedDocumentType || "";
    this.documentTypeSearchQuery = snap.documentTypeSearchQuery || "";
    if (this.selectedDocumentType) {
      this.uploadFilingDocForm.patchValue({
        document_type: this.selectedDocumentType,
      });
    }
    this.uploadedDocList = [];
    this.loadIasForFiling(() => {
      if (snap.selectedIaId != null) {
        this.selectedIa =
          this.iaList.find(
            (ia) => Number(ia.id) === Number(snap.selectedIaId),
          ) || null;
      } else {
        this.selectedIa = null;
      }
      if (snap.pendingEfilingDocumentId != null) {
        this.pendingDocumentFilingSubmit = {
          efilingDocumentId: Number(snap.pendingEfilingDocumentId),
          documentType: snap.selectedDocumentType || "",
          iaId: snap.selectedIaId ?? null,
        };
      } else {
        this.pendingDocumentFilingSubmit = null;
      }
      this.loadSelectedCaseDetailsAndDocs();
    });
  }

  private applyFilingMinimalAfterPayment(filing: any): void {
    this.get_document_index_for_existing_filing(filing.case_type.id);
    this.selectedFiling = filing;
    this.selectedEfilingId = Number(filing.id);
    this.selectedEfilingNumber = String(filing.e_filing_number ?? "");
    this.isDropdownOpen = false;
    this.searchQuery = "";
    const at = String(filing?.case_type?.annexure_type ?? "")
      .trim()
      .toUpperCase();
    this.litigantType = at === "A" ? "APPELLANT" : "PETITIONER";
    this.selectedIa = null;
    this.uploadedDocList = [];
    this.selectedDocumentType = "";
    this.documentTypeSearchQuery = "";
    this.uploadFilingDocForm.reset();
    this.pendingDocumentFilingSubmit = null;
    this.loadIasForFiling();
    this.loadSelectedCaseDetailsAndDocs();
  }

  /** True when fee is paid for the pending uploaded document (before Submit filing). */
  hasPaymentForPendingSubmit(): boolean {
    const p = this.pendingDocumentFilingSubmit;
    if (!p || !this.selectedEfilingId) return false;
    return this.hasValidUploadPaymentToken(
      p.documentType,
      p.iaId,
      p.efilingDocumentId,
    );
  }

  /** Submit filing is allowed only after upload + successful payment. */
  canClickSubmitFiling(): boolean {
    return (
      !!this.pendingDocumentFilingSubmit &&
      this.hasPaymentForPendingSubmit() &&
      !this.isSubmitDocumentFilingInProgress
    );
  }

  /** Pay court fee for the document already uploaded (pending submit). */
  async payCourtFeeForCurrentDocument(): Promise<void> {
    const p = this.pendingDocumentFilingSubmit;
    if (!this.selectedEfilingId || !this.selectedEfilingNumber) {
      this.toastr.error("Select a case first.");
      return;
    }
    if (!p) {
      this.toastr.error("Upload a document first, then pay the court fee.");
      return;
    }
    if (
      this.hasValidUploadPaymentToken(
        p.documentType,
        p.iaId,
        p.efilingDocumentId,
      )
    ) {
      this.toastr.info(
        "Court fee for this document is already paid. Click Submit filing to finish.",
        "",
        { timeOut: 5000, closeButton: true },
      );
      return;
    }
    this.isCourtFeePaymentInProgress = true;
    try {
      await this.executeCourtFeePaymentModal(
        p.documentType,
        p.iaId,
        p.efilingDocumentId,
      );
    } finally {
      this.isCourtFeePaymentInProgress = false;
    }
  }

  async submitDocumentFilingAfterPayment(): Promise<void> {
    const p = this.pendingDocumentFilingSubmit;
    if (!p || !this.selectedEfilingId) return;
    if (
      !this.hasValidUploadPaymentToken(
        p.documentType,
        p.iaId,
        p.efilingDocumentId,
      )
    ) {
      this.toastr.warning("Pay the court fee first.");
      return;
    }
    this.isSubmitDocumentFilingInProgress = true;
    try {
      await firstValueFrom(
        this.eFilingService.submitDocumentFilingAfterPayment(
          p.efilingDocumentId,
        ),
      );
      this.consumeUploadPaymentTokenAfterSuccessfulSubmit();
      this.pendingDocumentFilingSubmit = null;
      this.toastr.success("Document filing submitted.");
      this.loadSelectedCaseDetailsAndDocs();
    } catch (err) {
      console.error(err);
      const msg = getValidationErrorMessage(err);
      this.toastr.error(
        msg || "Could not submit filing. Ensure court fee payment completed.",
      );
    } finally {
      this.isSubmitDocumentFilingInProgress = false;
    }
  }

  /**
   * SweetAlert payment for document context. Online path redirects to gateway.
   * @returns true when offline payment saved; false if cancelled or online redirect.
   */
  private async executeCourtFeePaymentModal(
    documentType: string,
    iaId: number | null,
    efilingDocumentId: number,
  ): Promise<boolean> {
    if (this.hasValidUploadPaymentToken(documentType, iaId, efilingDocumentId)) {
      return true;
    }

    if (!this.selectedEfilingId || !this.selectedEfilingNumber) {
      this.toastr.error("Select a case before paying.");
      return false;
    }

    const iaLabel = this.selectedIa
      ? `IA ${this.escapeHtml(String(this.selectedIa.ia_number || ""))}`
      : "main filing";
    const html = `
      <p class="text-start small text-muted mb-2">Court fee for <strong>${this.escapeHtml(documentType)}</strong> (${iaLabel}) — e-filing <strong>${this.escapeHtml(this.selectedEfilingNumber)}</strong>.</p>
      <label class="d-block text-start small">Amount (INR)</label>
      <input id="swal-doc-pay-amount" type="number" class="swal2-input" min="0.01" step="0.01" placeholder="e.g. 250" />
      <div class="text-start mt-3 mb-1 small">Mode</div>
      <div class="d-flex gap-3 justify-content-start flex-wrap">
        <label class="mb-0"><input type="radio" name="swal-doc-pay-mode" id="swal-doc-pay-online" checked class="me-1" /> Online</label>
        <label class="mb-0"><input type="radio" name="swal-doc-pay-mode" id="swal-doc-pay-offline" class="me-1" /> Offline</label>
      </div>
      <div id="swal-doc-pay-offline-box" class="d-none mt-2 text-start">
        <input id="swal-doc-pay-txn" class="swal2-input mb-2" placeholder="Bank receipt no." />
        <input id="swal-doc-pay-date" type="date" class="swal2-input mb-2" />
        <input id="swal-doc-pay-file" type="file" accept="application/pdf,image/*" class="swal2-file" />
      </div>
    `;

    const result = await Swal.fire({
      title: "Court fee for this document",
      html,
      width: 480,
      showCancelButton: true,
      confirmButtonText: "Continue",
      cancelButtonText: "Cancel",
      didOpen: () => {
        const online = document.getElementById("swal-doc-pay-online");
        const offline = document.getElementById("swal-doc-pay-offline");
        const box = document.getElementById("swal-doc-pay-offline-box");
        const toggle = (): void => {
          if (!box) return;
          const off = (offline as HTMLInputElement)?.checked;
          box.classList.toggle("d-none", !off);
        };
        online?.addEventListener("change", toggle);
        offline?.addEventListener("change", toggle);
        const d = new Date().toISOString().slice(0, 10);
        const dateEl = document.getElementById(
          "swal-doc-pay-date",
        ) as HTMLInputElement | null;
        if (dateEl && !dateEl.value) dateEl.value = d;
        toggle();
      },
      preConfirm: () => {
        const amountEl = document.getElementById(
          "swal-doc-pay-amount",
        ) as HTMLInputElement | null;
        const amount = Number.parseFloat(
          String(amountEl?.value || "").replace(/,/g, ""),
        );
        if (!Number.isFinite(amount) || amount <= 0) {
          Swal.showValidationMessage(
            "Enter a valid court fee amount greater than zero.",
          );
          return false;
        }
        const offline = (
          document.getElementById("swal-doc-pay-offline") as HTMLInputElement
        )?.checked;
        if (!offline) {
          return { amount, mode: "online" as const };
        }
        const txnId = String(
          (document.getElementById("swal-doc-pay-txn") as HTMLInputElement)
            ?.value || "",
        ).trim();
        const paymentDate = String(
          (document.getElementById("swal-doc-pay-date") as HTMLInputElement)
            ?.value || "",
        ).trim();
        const file = (
          document.getElementById("swal-doc-pay-file") as HTMLInputElement
        )?.files?.[0];
        if (!txnId || !paymentDate || !file) {
          Swal.showValidationMessage(
            "Enter bank receipt number, date of payment, and upload the receipt.",
          );
          return false;
        }
        return {
          amount,
          mode: "offline" as const,
          txnId,
          paymentDate,
          file,
        };
      },
    });

    if (!result.isConfirmed || !result.value) return false;

    const v = result.value as
      | { amount: number; mode: "online" }
      | {
          amount: number;
          mode: "offline";
          txnId: string;
          paymentDate: string;
          file: File;
        };

    if (v.mode === "online") {
      const nonce = this.generateUploadNonce();
      this.persistDocumentFilingUiSnapshotForUploadPayment(
        documentType,
        iaId,
        nonce,
        efilingDocumentId,
      );
      const confirm = await Swal.fire({
        title: "Proceed to payment gateway?",
        html: `You will leave this page to pay <strong>₹${v.amount}</strong> for the uploaded document. When you return, click <strong>Submit filing</strong> to finish.`,
        icon: "question",
        showCancelButton: true,
        confirmButtonText: "Continue to pay",
        cancelButtonText: "Cancel",
      });
      if (!confirm.isConfirmed) return false;
      try {
        const init = await firstValueFrom(
          this.paymentService.initiate({
            amount: v.amount,
            application: this.selectedEfilingId,
            e_filing_number: this.selectedEfilingNumber,
            payment_type: "application",
            source: "document_filing",
            efiling_document_id: efilingDocumentId,
          }),
        );
        this.postToGateway(init.action, init.fields as Record<string, string>);
      } catch (e) {
        console.error(e);
        this.toastr.error("Could not start payment. Please try again.");
      }
      return false;
    }

    try {
      const res = await firstValueFrom(
        this.paymentService.submitOffline({
          application: this.selectedEfilingId,
          txn_id: v.txnId,
          court_fees: String(v.amount),
          payment_date: v.paymentDate,
          e_filing_number: this.selectedEfilingNumber || "",
          bank_receipt: v.file,
          payment_type: "Court Fees",
          efiling_document_id: efilingDocumentId,
          source: "document_filing",
        }),
      );
      this.saveUploadPaymentToken({
        eFilingId: this.selectedEfilingId,
        documentType,
        iaId,
        efilingDocumentId,
        uploadNonce: this.generateUploadNonce(),
        referenceNo: res?.reference_no || "",
        txnId: v.txnId,
        amount: String(v.amount),
        paymentMode: "offline",
        paidAt: Date.now(),
      });
      this.toastr.success(
        "Court fee recorded. Click Submit filing to finish.",
        "",
        { timeOut: 5000, closeButton: true },
      );
      return true;
    } catch (e) {
      console.error(e);
      this.toastr.error("Could not submit offline payment.");
      return false;
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

  async handleDocUpload(data: any): Promise<void> {
    if (this.isUploadingDocuments || this.isUploadRequestInFlight) return;
    this.isUploadRequestInFlight = true;
    try {
      const documentType = String(data?.document_type || "").trim();
      const uploadItems = Array.isArray(data?.items) ? data.items : [];

      if (
        !documentType ||
        uploadItems.length === 0 ||
        !this.selectedEfilingId
      ) {
        this.toastr.warning(
          "Please select an E-Filing and add documents with document type and index names.",
        );
        return;
      }

      // Validate PDF size (≤ 25 MB) and OCR before confirmation
      const files = uploadItems.map((i: any) => i.file).filter(Boolean);
      const { valid, errors } = validatePdfFiles(files);
      if (errors.length > 0) {
        this.toastr.error(errors.join(" "));
        return;
      }
      if (valid.length !== files.length) {
        this.toastr.error(
          "Some files could not be validated. Please ensure all files are PDFs under 25 MB.",
        );
        return;
      }

      const ocrError = await validatePdfOcrForFiles(valid);
      if (ocrError) {
        this.toastr.error(ocrError);
        return;
      }

      if (this.pendingDocumentFilingSubmit) {
        this.toastr.warning(
          "Pay the court fee and click Submit filing for the document already uploaded, or delete that document from the list above.",
          "",
          { timeOut: 8000, closeButton: true },
        );
        return;
      }

      const targetLabel = this.selectedIa
        ? `the selected IA (${this.selectedIa.ia_number || ""})`
        : "the selected e-filing";
      const proceed = await this.promptOtpAndProceed(
        "File Documents?",
        `Upload these documents to ${targetLabel}. Filing as ${this.litigantTypeLabel()}.`,
      );
      if (!proceed) return;

      this.isUploadingDocuments = true;
      this.uploadFileProgresses = uploadItems.map(() => 0);

      const documentPayload = new FormData();
      documentPayload.append("document_type", documentType);
      documentPayload.append("e_filing", String(this.selectedEfilingId));
      documentPayload.append("e_filing_number", this.selectedEfilingNumber);

      if (this.selectedIa) {
        documentPayload.append("is_ia", "true");
        documentPayload.append(
          "ia_number",
          String(this.selectedIa.ia_number ?? ""),
        );
      } else {
        documentPayload.append("is_ia", "false");
      }

      documentPayload.append("filed_by", this.litigantType);

      const documentRes = await firstValueFrom(
        this.eFilingService.upload_case_documnets(documentPayload),
      );
      const documentId = documentRes?.id;
      if (!documentId) throw new Error("Document creation failed");

      const existingIndexes = Array.isArray(documentRes?.document_indexes)
        ? documentRes.document_indexes
        : [];
      let nextSeq = this.maxDocumentSequence(existingIndexes);
      const uploadedDocumentParts: any[] = [];
      const groupName = String(data?.parent_group_name ?? "").trim();
      let parentIndexId: number | null = null;

      if (groupName) {
        nextSeq += 1;
        const parentFd = new FormData();
        parentFd.append("document", String(documentId));
        parentFd.append("document_part_name", groupName);
        parentFd.append("document_sequence", String(nextSeq));
        const parentRes = await firstValueFrom(
          this.eFilingService.createDocumentIndexMetadata(parentFd),
        );
        parentIndexId = parentRes?.id != null ? Number(parentRes.id) : null;
        if (parentRes) uploadedDocumentParts.push(parentRes);
      }

      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];
        nextSeq += 1;
        const indexPayload = new FormData();
        indexPayload.append("document", String(documentId));
        indexPayload.append(
          "document_part_name",
          String(item.index_name || "").trim(),
        );
        indexPayload.append("file_part_path", item.file);
        indexPayload.append("document_sequence", String(nextSeq));
        if (item.index_id) {
          indexPayload.append("index", String(item.index_id));
        }
        if (parentIndexId != null) {
          indexPayload.append("parent_document_index", String(parentIndexId));
        }

        const indexRes = await this.uploadIndexFileWithProgress(
          indexPayload,
          i,
        );
        uploadedDocumentParts.push(indexRes);
      }

      const firstFileUrl = uploadedDocumentParts.find(
        (p: any) => p?.file_url || p?.file_part_path,
      );
      this.uploadedDocList.push({
        ...documentRes,
        document_indexes: uploadedDocumentParts,
        final_document:
          firstFileUrl?.file_url ||
          firstFileUrl?.file_part_path ||
          documentRes?.final_document,
      });

      this.uploadCompletedToken++;
      const iaIdForPending =
        this.selectedIa?.id != null ? Number(this.selectedIa.id) : null;
      this.pendingDocumentFilingSubmit = {
        efilingDocumentId: Number(documentId),
        documentType,
        iaId: iaIdForPending,
      };
      this.toastr.success(
        "Documents uploaded. Pay the court fee, then click Submit filing.",
        "",
        { timeOut: 8000, closeButton: true },
      );
    } catch (error) {
      console.error("Document upload failed", error);
      const msg = getValidationErrorMessage(error);
      const friendlyMsg =
        !msg || /bad request|http error|400/i.test(msg)
          ? "Failed to upload documents. Please ensure all PDFs are under 25 MB and OCR-converted (searchable)."
          : msg;
      this.toastr.error(friendlyMsg);
    } finally {
      this.isUploadingDocuments = false;
      this.isUploadRequestInFlight = false;
    }
  }

  private async promptOtpAndProceed(
    title: string,
    text: string,
  ): Promise<boolean> {
    const confirmed = await Swal.fire({
      title,
      text,
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, Proceed",
      cancelButtonText: "Cancel",
    });
    if (!confirmed.isConfirmed) return false;

    this.toastr.success("OTP has been sent successfully.", "", {
      timeOut: 3000,
      closeButton: true,
    });

    let resolved = false;
    return new Promise<boolean>((resolve) => {
      const finish = (value: boolean) => {
        if (resolved) return;
        resolved = true;
        resolve(value);
      };

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
            Swal.close();
            finish(true);
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
      }).then((result) => {
        if (result.dismiss === Swal.DismissReason.cancel) finish(false);
      });
    });
  }

  /** Merge items from uploaded documents only (not existing docs). */
  private getMergeItems(): { url: string; name: string }[] {
    const items: { url: string; name: string }[] = [];
    const list = [...this.uploadedDocList];
    for (const doc of list) {
      const indexes = doc?.document_indexes;
      if (Array.isArray(indexes) && indexes.length > 0) {
        for (const part of indexes) {
          const url = part?.file_url || part?.file_part_path;
          if (url) {
            const name =
              part?.document_part_name?.trim() ||
              doc?.document_type ||
              "Document";
            items.push({ url, name });
          }
        }
      } else if (doc?.final_document) {
        const url = doc.final_document;
        const name = doc?.document_type?.trim() || "Document";
        items.push({ url, name });
      }
    }
    return items;
  }

  private toAbsoluteUrl(url: string): string {
    if (!url) return "";
    const s = String(url).trim();
    if (s.startsWith("http://") || s.startsWith("https://")) return s;
    const base = app_url.replace(/\/$/, "");
    return s.startsWith("/") ? `${base}${s}` : `${base}/${s}`;
  }

  canDownloadMerged(): boolean {
    return this.getMergeItems().length > 0;
  }

  downloadMergedPdf(): void {
    const items = this.getMergeItems();
    if (items.length === 0 || this.isMergingPdf) return;

    this.isMergingPdf = true;
    this.mergeError = null;

    const fetches = items.map((item) =>
      this.eFilingService.fetch_document_blob(this.toAbsoluteUrl(item.url)),
    );

    forkJoin(fetches).subscribe({
      next: (blobs) => {
        const files = blobs.map((blob, i) => {
          const name = items[i].name.replace(/\.pdf$/i, "") + ".pdf";
          return new File([blob], name, { type: "application/pdf" });
        });
        const names = items.map((i) => i.name);
        const row = this.filingsWithLitigants.find(
          (f) => f.filing.id === this.selectedEfilingId,
        );
        const litigants = row?.litigants ?? [];
        const pnFallback = String(
          this.selectedFiling?.petitioner_name || "",
        ).trim();
        const frontPage = {
          petitionerName: formatPartyLine(
            getOrderedPartyNames(litigants, true),
            pnFallback,
          ),
          respondentName: formatPartyLine(
            getOrderedPartyNames(litigants, false),
            "",
          ),
          caseNo: (this.selectedFiling?.e_filing_number || "").trim(),
          caseType:
            this.selectedFiling?.case_type?.full_form ||
            this.selectedFiling?.case_type?.type_name ||
            "",
        };

        this.eFilingService.mergePdfs(files, names, frontPage).subscribe({
          next: (mergedBlob) => {
            const url = URL.createObjectURL(mergedBlob);
            const a = document.createElement("a");
            a.href = url;
            const docType =
              (this.uploadedDocList[0]?.document_type || "Documents")
                .trim()
                .replace(/[^a-zA-Z0-9_-]/g, "_")
                .replace(/_+/g, "_")
                .replace(/^_|_$/g, "") || "Documents";
            const efilingNo =
              (this.selectedEfilingNumber || "").replace(
                /[^a-zA-Z0-9_-]/g,
                "",
              ) || "merged";
            a.download = `${docType}_${efilingNo}.pdf`;
            a.click();
            URL.revokeObjectURL(url);
            this.isMergingPdf = false;
          },
          error: (err) => {
            this.isMergingPdf = false;
            this.mergeError =
              err?.error?.error || err?.message || "Failed to merge PDFs.";
          },
        });
      },
      error: () => {
        this.isMergingPdf = false;
        this.mergeError = "Failed to fetch documents.";
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
}
