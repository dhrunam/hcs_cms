import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DomSanitizer, SafeResourceUrl } from "@angular/platform-browser";
import { ActivatedRoute, RouterLink } from "@angular/router";
import { firstValueFrom, forkJoin } from "rxjs";
import Swal from "sweetalert2";
import { ToastrService } from "ngx-toastr";
import {
  DistinctBenchOption,
  EfilingService,
} from "../../../../../services/advocate/efiling/efiling.services";
import { EfilingChatComponent } from "../../../../../shared/efiling-chat/efiling-chat";
import { catchError, of } from "rxjs";
import { PaymentService } from "../../../../../services/payment/payment.service";
import {
  EfilingDocumentIndexGroup,
  firstClickableEfilingDocumentIndexInGrouped,
  firstClickableEfilingDocumentIndexInList,
  groupEfilingDocumentIndexesByType,
  isEfilingDocumentIndexClickable,
  trackByEfilingDocumentIndexRowId,
} from "../../../../../utils/efiling-document-index-tree";

@Component({
  selector: "app-filed-case-details",
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EfilingChatComponent],
  templateUrl: "./details.html",
  styleUrl: "./details.css",
})
export class FiledCaseDetails {
  /**
   * Adobe / Chromium-style PDF fragment params to hide the viewer thumbnail/outline sidebar.
   * Applied to iframe src; support depends on the user's built-in PDF viewer.
   */
  private withPdfViewerNoSidepane(url: string): string {
    const u = String(url || "").trim();
    if (!u) return u;
    const hashIdx = u.indexOf("#");
    const add = "navpanes=0&pagemode=UseNone";
    if (hashIdx === -1) {
      return `${u}#${add}`;
    }
    const fragment = u.slice(hashIdx + 1);
    if (/(^|&)navpanes=/i.test(fragment)) {
      return u;
    }
    const joiner = fragment.length > 0 && !fragment.endsWith("&") ? "&" : "";
    return `${u.slice(0, hashIdx + 1)}${fragment}${joiner}${add}`;
  }

  private trustPdfPreviewUrl(url: string): SafeResourceUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl(
      this.withPdfViewerNoSidepane(url),
    );
  }

  readonly hiddenHistoryComments = new Set([
    "Document uploaded by advocate.",
    "Document re-uploaded by advocate.",
    "Document sent to scrutiny queue.",
    "Document review item created.",
  ]);

  filingId: number | null = null;
  filing: any = null;
  litigants: any[] = [];
  caseDetails: any = null;
  acts: any[] = [];
  documents: any[] = [];
  groupedDocuments: EfilingDocumentIndexGroup[] = [];
  selectedDocument: any = null;
  selectedDocumentUrl: SafeResourceUrl | null = null;
  selectedDocumentBlobUrl: string | null = null;
  documentHistory: any[] = [];
  scrutinyChecklist: any[] = [];
  distinctBenches: DistinctBenchOption[] = [];
  reviewNote = "";
  isLoading = false;

  isSavingReview = false;
  isSubmittingApprovedCase = false;
  missingFilingId = false;
  activeTab: "filing" | "documents" | "ia" | "chat" = "filing";
  iaList: any[] = [];
  fullScreen = false;
  iaDocuments: any[] = [];
  groupedIaDocuments: EfilingDocumentIndexGroup[] = [];
  selectedIaDocument: any = null;
  selectedIaDocumentUrl: SafeResourceUrl | null = null;
  selectedIaDocumentBlobUrl: string | null = null;
  isVerifyingIaId: number | null = null;
  paymentOutcome: "success" | "failed" | null = null;
  paymentDetails: {
    txnId?: string;
    paidAt?: string;
    referenceNo?: string;
    amount?: string;
    paymentMode?: "online" | "offline";
    bankReceipt?: string;
    paymentDate?: string;
  } | null = null;

  constructor(
    private route: ActivatedRoute,
    private efilingService: EfilingService,
    private paymentService: PaymentService,
    private sanitizer: DomSanitizer,
    private toastr: ToastrService,
  ) {}

  setActiveTab(tab: "filing" | "documents" | "ia" | "chat"): void {
    this.activeTab = tab;
  }

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      const rawId = params.get("id");
      const nextId = rawId ? Number(rawId) : null;
      this.filingId = nextId && !Number.isNaN(nextId) ? nextId : null;
      this.missingFilingId = !this.filingId;

      if (this.filingId) {
        this.loadWorkspace(this.filingId);
      }
    });
  }

  toogleScreen() {
    this.fullScreen = !this.fullScreen;

    if (this.fullScreen) {
      document.body.classList.add("fullscreen-mode");
    } else {
      document.body.classList.remove("fullscreen-mode");
    }
  }

  loadWorkspace(id: number, preferredDocumentId?: number): void {
    this.isLoading = true;

    forkJoin({
      filing: this.efilingService.get_filing_by_id(id),
      litigants: this.efilingService.get_litigant_list_by_filing_id(id),
      caseDetails: this.efilingService.get_case_details_by_filing_id(id),
      acts: this.efilingService.get_acts_by_filing_id(id),
      documents: this.efilingService.get_document_reviews_by_filing_id(
        id,
        false,
      ),
      iaDocuments: this.efilingService.get_document_reviews_by_filing_id(
        id,
        true,
      ),
      ias: this.efilingService.get_ias_by_efiling_id(id),
      payment: this.paymentService.latest(id).pipe(catchError(() => of(null))),
    }).subscribe({
      next: ({
        filing,
        litigants,
        caseDetails,
        acts,
        documents,
        iaDocuments,
        ias,
        payment,
      }) => {
        this.filing = filing;
        this.litigants = litigants?.results ?? [];
        this.caseDetails = caseDetails?.results?.[0] ?? null;
        this.acts = acts?.results ?? [];
        this.documents = documents?.results ?? [];
        this.groupedDocuments = this.groupDocumentsByType(this.documents);
        this.iaDocuments = iaDocuments?.results ?? [];
        this.groupedIaDocuments = this.groupDocumentsByType(this.iaDocuments);
        this.iaList = Array.isArray(ias) ? ias : (ias?.results ?? []);
        this.updatePaymentDetails(payment);
        const firstIaWithDocs = this.iaWithDocuments.find(
          (i) => i.documents.length > 0,
        );
        this.selectIaDocument(
          firstIaWithDocs
            ? this.firstClickableInGroupedDocs(firstIaWithDocs.groupedDocs)
            : null,
        );
        this.loadChecklist();
        const preferred =
          preferredDocumentId != null
            ? (this.documents.find((d) => d.id === preferredDocumentId) ?? null)
            : null;
        const initialDoc =
          preferred && this.isDocumentIndexClickable(preferred)
            ? preferred
            : this.firstClickableInDocList(this.documents);
        this.selectDocument(initialDoc ?? null);
        this.isLoading = false;
      },
      error: (error) => {
        console.error("Failed to load scrutiny workspace", error);
        this.isLoading = false;
      },
    });
  }

  private updatePaymentDetails(tx: any): void {
    if (!tx || (!tx.txn_id && !tx.reference_no && !tx.status)) {
      this.paymentOutcome = null;
      this.paymentDetails = null;
      return;
    }
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
    } else {
      this.paymentOutcome = null;
    }
    this.paymentDetails = {
      txnId: tx.txn_id || undefined,
      paidAt: tx.payment_datetime || tx.paid_at || undefined,
      referenceNo: tx.reference_no || undefined,
      amount: tx.amount || tx.court_fees || undefined,
      paymentMode,
      bankReceipt: tx.bank_receipt || undefined,
      paymentDate: tx.payment_date || undefined,
    };
  }

  loadChecklist(): void {
    const caseTypeId = this.filing?.case_type?.id;
    if (!caseTypeId) {
      this.scrutinyChecklist = [];
      return;
    }

    this.efilingService.get_file_scrutiny_checklist(caseTypeId).subscribe({
      next: (data) => {
        this.scrutinyChecklist = data?.results ?? data ?? [];
      },
      error: () => {
        this.scrutinyChecklist = [];
      },
    });
  }

  selectDocument(document: any): void {
    this.selectedDocument = document;
    this.reviewNote = document?.draft_comments ?? document?.comments ?? "";
    this.updatePreviewUrl(document ?? null);

    if (!document?.id) {
      this.documentHistory = [];
      return;
    }

    this.efilingService.get_document_scrutiny_history(document.id).subscribe({
      next: (data) => {
        this.documentHistory = data?.results ?? data ?? [];
      },
      error: () => {
        this.documentHistory = [];
      },
    });
  }

  updatePreviewUrl(document: any | null): void {
    if (this.selectedDocumentBlobUrl) {
      URL.revokeObjectURL(this.selectedDocumentBlobUrl);
      this.selectedDocumentBlobUrl = null;
    }

    const docId = Number(document?.id || 0);
    const fileUrl = document?.file_url ? document.file_url : null;
    if (!docId && !fileUrl) {
      this.selectedDocumentUrl = null;
      return;
    }

    if (fileUrl) {
      this.selectedDocumentUrl = this.trustPdfPreviewUrl(fileUrl);
    }
    const stream$ = docId
      ? this.efilingService.fetch_document_blob_by_index(docId)
      : this.efilingService.fetch_document_blob(fileUrl);
    stream$.subscribe({
      next: (blob) => {
        this.selectedDocumentBlobUrl = URL.createObjectURL(blob);
        this.selectedDocumentUrl = this.trustPdfPreviewUrl(
          this.selectedDocumentBlobUrl,
        );
      },
      error: () => {
        if (fileUrl) {
          this.selectedDocumentUrl = this.trustPdfPreviewUrl(fileUrl);
        } else {
          this.selectedDocumentUrl = null;
        }
      },
    });
  }

  groupDocumentsByType(docs: any[]): EfilingDocumentIndexGroup[] {
    return groupEfilingDocumentIndexesByType(docs);
  }

  isDocumentIndexClickable(doc: any): boolean {
    return isEfilingDocumentIndexClickable(doc);
  }

  officerDocumentRowClick(doc: any): void {
    if (!this.isDocumentIndexClickable(doc)) return;
    this.selectDocument(doc);
  }

  officerDocumentRowKeydown(event: Event, doc: any): void {
    if (!this.isDocumentIndexClickable(doc)) return;
    event.preventDefault();
    this.selectDocument(doc);
  }

  officerIaDocumentRowClick(doc: any): void {
    if (!this.isDocumentIndexClickable(doc)) return;
    this.selectIaDocument(doc);
  }

  officerIaDocumentRowKeydown(event: Event, doc: any): void {
    if (!this.isDocumentIndexClickable(doc)) return;
    event.preventDefault();
    this.selectIaDocument(doc);
  }

  private firstClickableInDocList(docs: any[]): any | null {
    return firstClickableEfilingDocumentIndexInList(docs);
  }

  private firstClickableInGroupedDocs(
    grouped: EfilingDocumentIndexGroup[],
  ): any | null {
    return firstClickableEfilingDocumentIndexInGrouped(grouped);
  }

  readonly trackByRowDocumentId = trackByEfilingDocumentIndexRowId;

  acceptDocument(): void {
    this.submitReview("ACCEPTED");
  }

  rejectDocument(): void {
    // Rejecting a document also persists the current notes in the same review update.
    this.submitReview("REJECTED");
  }

  async onRegisterCaseClick(): Promise<void> {
    if (
      !this.canSubmitApprovedFiling ||
      !this.filingId ||
      !this.allDocumentsAccepted
    )
      return;

    const benchOptions = await this.getBenchInputOptions();
    if (!benchOptions) {
      return;
    }

    Swal.fire({
      title: "Register Case & Assign Bench",
      text: "Please select the Bench (Judge) this case will be assigned to.",
      input: "select",
      inputOptions: benchOptions,
      inputPlaceholder: "-- Choose Bench --",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Register Case",
      cancelButtonText: "Cancel",
      confirmButtonColor: "#0d6efd",
      inputValidator: (value) => {
        return new Promise((resolve) => {
          if (value) {
            resolve(null);
          } else {
            resolve("Please select a bench");
          }
        });
      },
    }).then((result) => {
      if (result.isConfirmed) {
        this.submitApprovedFiling(result.value);
      }
    });
  }

  private async getBenchInputOptions(): Promise<Record<string, string> | null> {
    try {
      const benches = await firstValueFrom(
        this.efilingService.get_distinct_benches(),
      );
      this.distinctBenches = Array.isArray(benches) ? benches : [];

      const inputOptions = this.distinctBenches.reduce<Record<string, string>>(
        (options, bench) => {
          const benchCode = String(bench?.bench_code ?? "").trim();
          if (!benchCode || options[benchCode]) {
            return options;
          }

          const benchName = String(bench?.bench_name ?? "").trim();
          options[benchCode] = benchName
            ? `${benchCode} - ${benchName}`
            : benchCode;
          return options;
        },
        {},
      );

      if (Object.keys(inputOptions).length === 0) {
        this.toastr.error("No benches are available for assignment.");
        return null;
      }

      return inputOptions;
    } catch (error) {
      console.error("Failed to load distinct benches", error);
      this.toastr.error("Unable to load benches right now.");
      return null;
    }
  }

  onSubmitReviewClick(): void {
    if (
      !this.canSubmitApprovedFiling ||
      !this.filingId ||
      this.allDocumentsAccepted
    )
      return;

    Swal.fire({
      title: "Submit Review?",
      html: "Your review decisions will be submitted. The advocate will be notified. The case will not be registered since some documents were rejected.",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, Submit",
      cancelButtonText: "Cancel",
      confirmButtonColor: "#0d6efd",
      cancelButtonColor: "#6c757d",
    }).then((result) => {
      if (result.isConfirmed) {
        this.submitApprovedFiling();
      }
    });
  }

  submitApprovedFiling(bench?: string): void {
    if (!this.canSubmitApprovedFiling || !this.filingId) {
      return;
    }

    this.isSubmittingApprovedCase = true;

    this.efilingService.submit_approved_filing(this.filingId, bench).subscribe({
      next: (filing) => {
        this.isSubmittingApprovedCase = false;
        this.filing = filing;
        this.toastr.success(
          this.filing?.case_number
            ? "Case registered successfully."
            : "Review submitted. Advocate has been notified.",
        );
        this.loadWorkspace(this.filingId!);
      },
      error: (error) => {
        console.error("Failed to submit approved filing", error);
        this.isSubmittingApprovedCase = false;
      },
    });
  }

  submitReview(status: string): void {
    if (
      !this.canReviewDocuments ||
      !this.selectedDocument?.id ||
      !this.filingId ||
      this.isSavingReview
    ) {
      return;
    }

    const currentDocumentId = this.selectedDocument.id;
    this.isSavingReview = true;
    this.efilingService
      .review_document(currentDocumentId, {
        comments: this.reviewNote,
        scrutiny_status: status,
      })
      .subscribe({
        next: (updatedDocument) => {
          this.isSavingReview = false;
          this.applyReviewedDocument(updatedDocument);
          const nextDocument = this.getNextDocumentForReview(currentDocumentId);
          this.selectDocument(
            nextDocument ??
              this.documents.find((d) => d.id === currentDocumentId) ??
              null,
          );
          this.refreshFilingSummary();
        },
        error: (error) => {
          console.error("Failed to update review", error);
          this.isSavingReview = false;
        },
      });
  }

  openInNewTab(): void {
    if (this.selectedDocument?.file_url) {
      window.open(this.selectedDocument.file_url, "_blank", "noopener");
    }
  }

  get filingStatusForDisplay(): string | null {
    const allActive = [...this.activeDocuments, ...this.activeIaDocuments];
    if (!allActive.length) {
      return this.filing?.status ?? null;
    }

    const tones = allActive.map((doc) =>
      this.getStatusTone(this.getEffectiveReviewStatus(doc)),
    );

    if (tones.every((tone) => tone === "success")) {
      // Only show ACCEPTED when case is registered. Until then, show Under Scrutiny
      // so the status does not change to Accepted until "Register Case" is clicked.
      if (this.isCaseRegistered) {
        return "ACCEPTED";
      }
      return "UNDER_SCRUTINY";
    }

    if (tones.includes("danger")) {
      const hasNonRejected = tones.some((tone) => tone !== "danger");
      return hasNonRejected ? "PARTIALLY_REJECTED" : "REJECTED";
    }

    return this.filing?.status ?? "UNDER_SCRUTINY";
  }

  getStatusLabel(status: string | null): string {
    const normalizedStatus = (status ?? "").trim().toLowerCase();
    if (
      !normalizedStatus ||
      normalizedStatus === "submitted" ||
      normalizedStatus === "under_scrutiny"
    ) {
      return "Under Scrutiny";
    }
    if (normalizedStatus.includes("accept")) {
      return "Accepted";
    }
    if (
      normalizedStatus.includes("reject") ||
      normalizedStatus.includes("object")
    ) {
      return "Rejected";
    }
    if (normalizedStatus.includes("partially")) {
      return "Partially Rejected";
    }
    if (normalizedStatus === "draft") {
      return "Draft";
    }
    return status ?? "Under Scrutiny";
  }

  getStatusTone(status: string | null): "warning" | "success" | "danger" {
    const label = this.getStatusLabel(status).toLowerCase();
    if (label.includes("accept")) {
      return "success";
    }
    if (label.includes("reject") || label.includes("object")) {
      return "danger";
    }
    return "warning";
  }

  getStatusClass(status: string | null): string {
    const tone = this.getStatusTone(status);
    if (tone === "success") {
      return "status-badge-success";
    }
    if (tone === "danger") {
      return "status-badge-danger";
    }
    return "status-badge-warning";
  }

  getDocumentStatusLabel(document: any): string {
    const draftStatus = (document?.draft_scrutiny_status ?? "").trim();
    if (draftStatus) {
      const baseLabel = this.getStatusLabel(draftStatus);
      return baseLabel === "Under Scrutiny" ? baseLabel : `Draft ${baseLabel}`;
    }
    return this.getStatusLabel(document?.scrutiny_status ?? null);
  }

  getDocumentStatusClass(document: any): string {
    const draftStatus = (document?.draft_scrutiny_status ?? "").trim();
    return this.getStatusClass(
      draftStatus || document?.scrutiny_status || null,
    );
  }

  private extractFileName(value: string | null | undefined): string {
    const raw = (value ?? "").trim();
    if (!raw) return "";

    const withoutQuery = raw.split("?")[0];
    const parts = withoutQuery.split("/");
    return parts[parts.length - 1] || "";
  }

  getDocumentTitle(document: any): string {
    const partName = (document?.document_part_name ?? "").trim();
    if (partName) return partName;

    const fileUrl = document?.file_url ?? document?.file_part_path;
    const fileName = this.extractFileName(fileUrl);
    return fileName || "Uploaded document";
  }

  getDocumentMeta(document: any): string {
    return "PDF document";
  }

  getDocumentDate(document: any): string | null {
    return (
      document?.last_reviewed_at ??
      document?.last_resubmitted_at ??
      document?.updated_at ??
      null
    );
  }

  historyClass(status: string | null): string {
    const tone = this.getStatusTone(status);
    if (tone === "success") {
      return "history-success";
    }
    if (tone === "danger") {
      return "history-danger";
    }
    return "history-warning";
  }

  trackById(_: number, item: any): number {
    return item.id;
  }

  trackByGroupIndex(index: number, group: any): string {
    return `${index}__${group?.document_type ?? "unknown"}`;
  }

  get visibleDocumentHistory(): any[] {
    return this.documentHistory.filter((item) => {
      const comment = (item?.comments ?? "").trim();
      return Boolean(comment) && !this.hiddenHistoryComments.has(comment);
    });
  }

  get sortedLitigants(): any[] {
    return [...this.litigants].sort(
      (a, b) => (a?.sequence_number ?? 0) - (b?.sequence_number ?? 0),
    );
  }

  get petitioners(): any[] {
    return this.sortedLitigants.filter((litigant) => litigant.is_petitioner);
  }

  get respondents(): any[] {
    return this.sortedLitigants.filter((litigant) => !litigant.is_petitioner);
  }

  get acceptedCount(): number {
    return this.activeDocuments.filter(
      (document) =>
        this.getStatusTone(this.getEffectiveReviewStatus(document)) ===
        "success",
    ).length;
  }

  get rejectedCount(): number {
    return this.activeDocuments.filter(
      (document) =>
        this.getStatusTone(this.getEffectiveReviewStatus(document)) ===
        "danger",
    ).length;
  }

  get pendingCount(): number {
    return this.activeDocuments.filter((document) =>
      this.isPendingDraftReview(document),
    ).length;
  }
  getActName(act: any): string {
    return act?.act?.actname ?? act?.actname ?? "-";
  }

  selectIaDocument(document: any): void {
    this.selectedIaDocument = document;
    this.reviewNoteIa = document?.draft_comments ?? document?.comments ?? "";
    if (this.selectedIaDocumentBlobUrl) {
      URL.revokeObjectURL(this.selectedIaDocumentBlobUrl);
      this.selectedIaDocumentBlobUrl = null;
    }
    const docId = Number(document?.id || 0);
    const fileUrl = document?.file_url ?? null;
    if (!docId && !fileUrl) {
      this.selectedIaDocumentUrl = null;
      return;
    }
    if (fileUrl) {
      this.selectedIaDocumentUrl = this.trustPdfPreviewUrl(fileUrl);
    }
    const stream$ = docId
      ? this.efilingService.fetch_document_blob_by_index(docId)
      : this.efilingService.fetch_document_blob(fileUrl);
    stream$.subscribe({
      next: (blob) => {
        this.selectedIaDocumentBlobUrl = URL.createObjectURL(blob);
        this.selectedIaDocumentUrl = this.trustPdfPreviewUrl(
          this.selectedIaDocumentBlobUrl,
        );
      },
      error: () => {
        if (fileUrl) {
          this.selectedIaDocumentUrl = this.trustPdfPreviewUrl(fileUrl);
        } else {
          this.selectedIaDocumentUrl = null;
        }
      },
    });

    if (!document?.id) {
      this.documentHistoryIa = [];
      return;
    }
    this.efilingService.get_document_scrutiny_history(document.id).subscribe({
      next: (data) => {
        this.documentHistoryIa = data?.results ?? data ?? [];
      },
      error: () => {
        this.documentHistoryIa = [];
      },
    });
  }

  reviewNoteIa = "";
  documentHistoryIa: any[] = [];
  isSavingReviewIa = false;

  acceptIaDocument(): void {
    this.submitIaReview("ACCEPTED");
  }

  rejectIaDocument(): void {
    this.submitIaReview("REJECTED");
  }

  private submitIaReview(status: string): void {
    if (
      !this.canReviewDocuments ||
      !this.selectedIaDocument?.id ||
      !this.filingId ||
      this.isSavingReviewIa
    ) {
      return;
    }

    const currentDocumentId = this.selectedIaDocument.id;
    this.isSavingReviewIa = true;
    this.efilingService
      .review_document(currentDocumentId, {
        comments: this.reviewNoteIa,
        scrutiny_status: status,
      })
      .subscribe({
        next: (updatedDocument) => {
          this.isSavingReviewIa = false;
          this.applyReviewedIaDocument(updatedDocument);
          const updatedDoc = this.iaDocuments.find(
            (d) => d.id === currentDocumentId,
          );
          if (updatedDoc) {
            this.selectIaDocument(updatedDoc);
          }
          this.refreshFilingSummary();
        },
        error: (error) => {
          console.error("Failed to update IA document review", error);
          this.isSavingReviewIa = false;
        },
      });
  }

  private applyReviewedIaDocument(updatedDocument: any): void {
    if (!updatedDocument?.id) return;
    this.iaDocuments = this.iaDocuments.map((doc) =>
      doc.id === updatedDocument.id ? { ...doc, ...updatedDocument } : doc,
    );
    this.groupedIaDocuments = this.groupDocumentsByType(this.iaDocuments);
  }

  get visibleDocumentHistoryIa(): any[] {
    return this.documentHistoryIa.filter((item) => {
      const comment = (item?.comments ?? "").trim();
      return Boolean(comment) && !this.hiddenHistoryComments.has(comment);
    });
  }

  getDocumentFileLabel(document: any): string {
    return this.getDocumentTitle(document);
  }

  getIaReliefStatus(item: {
    ia: any;
    documents: any[];
  }): "ACCEPTED" | "REJECTED" | "PENDING" {
    const savedStatus = this.getNormalizedStatus(item?.ia?.status);
    if (savedStatus.includes("accept")) {
      return "ACCEPTED";
    }
    if (savedStatus.includes("reject") || savedStatus.includes("object")) {
      return "REJECTED";
    }

    const docs = item?.documents ?? [];
    if (!docs.length) {
      return "PENDING";
    }

    const allAccepted = docs.every(
      (doc) =>
        this.getStatusTone(this.getEffectiveReviewStatus(doc)) === "success",
    );
    if (allAccepted) {
      return "ACCEPTED";
    }

    const hasRejected = docs.some(
      (doc) =>
        this.getStatusTone(this.getEffectiveReviewStatus(doc)) === "danger",
    );
    if (hasRejected) {
      return "REJECTED";
    }

    return "PENDING";
  }

  getIaReliefStatusLabel(item: { ia: any; documents: any[] }): string {
    const status = this.getIaReliefStatus(item);
    if (status === "PENDING") {
      return "Pending";
    }
    return this.getStatusLabel(status);
  }

  getIaReliefStatusClass(item: { ia: any; documents: any[] }): string {
    const status = this.getIaReliefStatus(item);
    if (status === "PENDING") {
      return "status-badge-warning";
    }
    return this.getStatusClass(status);
  }

  get iaWithDocuments(): Array<{
    ia: any;
    documents: any[];
    groupedDocs: EfilingDocumentIndexGroup[];
  }> {
    return this.iaList.map((ia) => {
      const iaNum = (ia?.ia_number ?? "").trim();
      const documents = this.iaDocuments.filter(
        (doc) => ((doc?.ia_number ?? "").trim() || null) === (iaNum || null),
      );
      return {
        ia,
        documents,
        groupedDocs: this.groupDocumentsByType(documents),
      };
    });
  }

  trackByIaItem(_: number, item: { ia: any }): number {
    return item?.ia?.id ?? 0;
  }

  getIaStatusBadgeClass(status: string | null): string {
    const s = (status ?? "").trim().toLowerCase();
    if (s.includes("accept")) return "status-badge-success";
    if (s.includes("reject") || s.includes("partial"))
      return "status-badge-danger";
    return "status-badge-warning";
  }

  getIaStatusLabel(status: string | null): string {
    const s = (status ?? "").trim().toLowerCase();
    if (!s) return "Pending";
    if (
      s.includes("under_scrutiny") ||
      s === "under scrutiny" ||
      s.includes("submitted")
    )
      return "Under Scrutiny";
    if (s.includes("accept")) return "Accepted";
    if (s.includes("reject") || s.includes("partial")) return "Rejected";
    return status ?? "Under Scrutiny";
  }

  canVerifyIa(ia: any): boolean {
    if (!ia?.id) return false;
    const s = (ia?.status ?? "").trim().toLowerCase();
    return !s.includes("accept");
  }

  verifyIa(ia: any): void {
    if (!ia?.id || !this.canVerifyIa(ia)) return;
    const iaLabel = ia?.ia_number || ia?.id || "this IA";
    Swal.fire({
      title: "Verify IA?",
      html: `Are you sure you want to verify <strong>IA ${iaLabel}</strong>? The status will be set to Accepted.`,
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, Verify",
      cancelButtonText: "Cancel",
      confirmButtonColor: "#198754",
      cancelButtonColor: "#6c757d",
    }).then((result) => {
      if (!result.isConfirmed) return;
      this.isVerifyingIaId = ia.id;
      this.efilingService.verify_ia(ia.id).subscribe({
        next: () => {
          this.toastr.success("IA verified successfully.");
          this.isVerifyingIaId = null;
          if (this.filingId) {
            this.efilingService.get_ias_by_efiling_id(this.filingId).subscribe({
              next: (data) => {
                this.iaList = Array.isArray(data)
                  ? data
                  : (data?.results ?? []);
              },
            });
          }
        },
        error: (err) => {
          this.toastr.error(
            err?.error?.detail || err?.message || "Failed to verify IA.",
          );
          this.isVerifyingIaId = null;
        },
      });
    });
  }

  selectedIaDocumentBelongsToIa(item: { documents: any[] }): boolean {
    if (!this.selectedIaDocument?.id || !item?.documents?.length) return false;
    return item.documents.some((d) => d?.id === this.selectedIaDocument?.id);
  }

  isDocumentAccepted(doc: any): boolean {
    if (!doc) return false;
    const status = doc?.draft_scrutiny_status || doc?.scrutiny_status || "";
    const norm = (status ?? "").trim().toLowerCase();
    return norm.includes("accept");
  }

  isIaDocumentAccepted(doc: any): boolean {
    return this.isDocumentAccepted(doc);
  }
  private applyReviewedDocument(updatedDocument: any): void {
    if (!updatedDocument?.id) {
      return;
    }

    this.documents = this.documents.map((document) =>
      document.id === updatedDocument.id
        ? { ...document, ...updatedDocument }
        : document,
    );
    this.groupedDocuments = this.groupDocumentsByType(this.documents);
  }

  private refreshFilingSummary(): void {
    if (!this.filingId) {
      return;
    }

    this.efilingService.get_filing_by_id(this.filingId).subscribe({
      next: (filing) => {
        this.filing = filing;
      },
      error: (error) => {
        console.error("Failed to refresh filing summary", error);
      },
    });
  }

  private getNextDocumentForReview(currentDocumentId: number): any {
    const clickable = (d: any) => isEfilingDocumentIndexClickable(d);
    const nextPendingDocument =
      this.documents.find(
        (document) =>
          document.id !== currentDocumentId &&
          this.isPendingDraftReview(document) &&
          clickable(document),
      ) ?? null;

    if (nextPendingDocument) {
      return nextPendingDocument;
    }

    const currentIndex = this.documents.findIndex(
      (document) => document.id === currentDocumentId,
    );
    const findNeighbor = (from: number, step: number): any | null => {
      for (
        let i = from + step;
        i >= 0 && i < this.documents.length;
        i += step
      ) {
        const d = this.documents[i];
        if (clickable(d)) return d;
      }
      return null;
    };

    if (currentIndex === -1) {
      return this.firstClickableInDocList(this.documents);
    }

    return (
      findNeighbor(currentIndex, 1) ??
      findNeighbor(currentIndex, -1) ??
      (clickable(this.documents[currentIndex])
        ? this.documents[currentIndex]
        : null)
    );
  }

  get allDocumentsReviewed(): boolean {
    const allActive = [...this.activeDocuments, ...this.activeIaDocuments];
    return (
      allActive.length > 0 &&
      allActive.every((document) => !this.isPendingDraftReview(document))
    );
  }

  /** All documents (main + IA) are accepted – no rejections. */
  get allDocumentsAccepted(): boolean {
    const allActive = [...this.activeDocuments, ...this.activeIaDocuments];
    if (allActive.length === 0) return false;
    return allActive.every(
      (doc) =>
        this.getStatusTone(this.getEffectiveReviewStatus(doc)) === "success",
    );
  }

  /** Case is registered with the court. */
  get isCaseRegistered(): boolean {
    return Boolean(this.filing?.case_number);
  }

  get isReturned(): boolean {
    const b = this.filing?.bench;
    return (
      this.isCaseRegistered &&
      (!b || b === "null" || b === "undefined" || b === "None")
    );
  }

  get canReviewDocuments(): boolean {
    if (!this.isCaseRegistered) {
      return true;
    }
    return this.hasPendingReviewItems;
  }

  get canSubmitApprovedFiling(): boolean {
    if (!this.filingId || this.isSubmittingApprovedCase) {
      return false;
    }

    if (this.isReturned) {
      return true;
    }

    if (!this.isCaseRegistered) {
      return this.allDocumentsReviewed;
    }

    // For already-registered cases, keep submit active throughout the
    // new review cycle (pending or already reviewed items), until submit.
    return this.hasReviewCycleItems;
  }

  get submitReviewButtonLabel(): string {
    if (this.isSubmittingApprovedCase) {
      return "Submitting...";
    }
    if (this.isCaseRegistered) {
      return this.hasReviewCycleItems ? "Submit New Review" : "Submitted";
    }
    return "Submit Review";
  }

  private isPendingDraftReview(document: any): boolean {
    const draftStatus = this.getNormalizedStatus(
      document?.draft_scrutiny_status,
    );
    if (["accepted", "rejected"].includes(draftStatus)) {
      return false;
    }
    const finalStatus = this.getNormalizedStatus(document?.scrutiny_status);
    return !["accepted", "rejected"].includes(finalStatus);
  }

  private getEffectiveReviewStatus(document: any): string | null {
    return document?.draft_scrutiny_status || document?.scrutiny_status || null;
  }

  private getNormalizedStatus(status: string | null | undefined): string {
    return String(status ?? "")
      .trim()
      .toLowerCase();
  }

  private get activeDocuments(): any[] {
    const explicitlyActive = this.documents.filter(
      (document) => document?.is_active !== false,
    );
    return explicitlyActive.length > 0 ? explicitlyActive : this.documents;
  }

  private get activeIaDocuments(): any[] {
    const explicitlyActive = this.iaDocuments.filter(
      (document) => document?.is_active !== false,
    );
    return explicitlyActive.length > 0 ? explicitlyActive : this.iaDocuments;
  }

  private get reviewCycleDocuments(): any[] {
    const allActive = [...this.activeDocuments, ...this.activeIaDocuments];
    return allActive.filter((document) => {
      const hasDraftStatus = Boolean(
        String(document?.draft_scrutiny_status ?? "").trim(),
      );
      return Boolean(document?.is_new_for_scrutiny) || hasDraftStatus;
    });
  }

  private get hasPendingReviewItems(): boolean {
    return this.reviewCycleDocuments.some((document) =>
      this.isPendingDraftReview(document),
    );
  }

  private get hasReviewCycleItems(): boolean {
    return this.reviewCycleDocuments.length > 0;
  }

  private get allReviewCycleItemsReviewed(): boolean {
    return (
      this.reviewCycleDocuments.length > 0 &&
      this.reviewCycleDocuments.every(
        (document) => !this.isPendingDraftReview(document),
      )
    );
  }
}
