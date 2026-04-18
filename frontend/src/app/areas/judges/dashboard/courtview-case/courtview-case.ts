import { CommonModule } from "@angular/common";
import { Component, OnInit, OnDestroy, ViewChild } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ActivatedRoute, Router, RouterLink } from "@angular/router";
import Swal from "sweetalert2";

import { CourtroomService } from "../../../../services/judge/courtroom.service";
import { benchLabel } from "../../../listing-officers/shared/bench-labels";
import { PdfAnnotatorComponent } from "../courtroom/pdf-annotator.component";
import { DomSanitizer, SafeHtml } from "@angular/platform-browser";
import { OfficeNoteEditor } from "../../../office-note-sheet/note-editor/note-editor";
import { buildCollapsedDisplaySections, DocumentDisplaySection, orderDocumentsForDisplay } from "../../../../shared/document-groups";

@Component({
  selector: "app-judge-courtview-case",
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, PdfAnnotatorComponent, OfficeNoteEditor],
  templateUrl: "./courtview-case.html",
  styleUrl: "./courtview-case.css",
})
export class JudgeCourtviewCasePage implements OnInit, OnDestroy {
  @ViewChild(PdfAnnotatorComponent) annotator?: PdfAnnotatorComponent;
  benchLabel = benchLabel;
  activeTab: 'details' | 'notes' = 'details';
  efilingId: number | null = null;
  forwardedForDate: string | null = null;

  isLoading = false;
  loadError = "";

  caseSummary: any = null;
  allCaseDocuments: any[] = [];
  orderEntries: any[] = [];

  previewDocument: any = null;
  previewDocumentBlobUrl: string | null = null;
  previewLoadError = "";

  documentSearchQuery: string = "";

  canWrite = false;

  activeShare: any = null;
  isSyncEnabled = false;
  private pollingInterval: any = null;
  private originalState: { doc: any; pageIndex: number } | null = null;
  /** Skip redundant follow updates when advocate position unchanged. */
  private lastAppliedSyncKey: string | null = null;
  /** Target page index until the PDF viewer has pages and can scroll. */
  private pendingSyncPage: number | null = null;
  private expandedVakalatGroupIds = new Set<string>();

  constructor(
    private route: ActivatedRoute,
    private courtroomService: CourtroomService,
    private router: Router,
    private sanitizer: DomSanitizer,
  ) {}

  ngOnInit(): void {
    this.canWrite = true;

    // Date is fixed essentially to today since we removed picker, but we still pick it up from query param
    // to strictly identify the correct forward row.
    const idRaw = this.route.snapshot.paramMap.get("id");
    this.efilingId = idRaw ? Number(idRaw) : null;
    this.forwardedForDate =
      this.route.snapshot.queryParamMap.get("forwarded_for_date");

    if (!this.efilingId || !this.forwardedForDate) {
      this.loadError = "Missing case id or forwarded_for_date.";
      return;
    }

    this.loadCaseSummary();
    this.startPolling();
  }

  ngOnDestroy(): void {
    this.stopPolling();
  }

  setActiveTab(tab: 'details' | 'notes'): void {
    this.activeTab = tab;
  }

  private startPolling() {
    this.pollingInterval = setInterval(() => {
      if (this.efilingId) {
        this.courtroomService.getActiveSharedView(this.efilingId).subscribe({
          next: (share: any) => {
            this.activeShare = share.active ? share : null;
            if (!this.activeShare) {
              this.lastAppliedSyncKey = null;
            }
            if (this.isSyncEnabled && this.activeShare) {
              this.applySync(false);
            }
          },
        });
      }
    }, 3000);
  }

  private stopPolling() {
    if (this.pollingInterval) clearInterval(this.pollingInterval);
  }

  toggleSync() {
    this.isSyncEnabled = !this.isSyncEnabled;
    if (this.isSyncEnabled) {
      if (!this.activeShare) {
        Swal.fire({
          title: "No Advocate Share",
          text: "Wait for the advocate to share their screen before enabling sync.",
          icon: "info",
          toast: true,
          position: "top-end",
          timer: 2000,
          showConfirmButton: false,
        });
        this.isSyncEnabled = false;
        return;
      }
      // Save current state
      this.originalState = {
        doc: this.previewDocument,
        pageIndex: this.annotator?.currentPageIndex || 0,
      };
      this.applySync(true);
    } else {
      this.lastAppliedSyncKey = null;
      this.pendingSyncPage = null;
      // Restore original state
      if (this.originalState) {
        this.selectPreviewDocument(this.originalState.doc);
        const targetPage = this.originalState.pageIndex;
        setTimeout(() => {
          this.annotator?.scrollToPage(targetPage);
          this.originalState = null;
        }, 500);
      }
    }
  }

  private applySync(force: boolean) {
    if (!this.activeShare) return;

    const docId = Number(this.activeShare.document_index_id);
    const pageIdx = Math.max(0, Number(this.activeShare.page_index) || 0);
    const key = `${docId}:${pageIdx}`;
    if (!force && key === this.lastAppliedSyncKey) {
      return;
    }

    if (Number(this.previewDocument?.id) !== docId) {
      const targetDoc = this.allCaseDocuments.find(
        (d) => Number(d.id) === docId,
      );
      if (targetDoc) {
        this.pendingSyncPage = pageIdx;
        this.selectPreviewDocument(targetDoc, true);
      }
      return;
    }

    this.pendingSyncPage = pageIdx;
    this.flushPendingSyncScroll(key);
  }

  /** Called when the PDF annotator finishes loading (e.g. after switching pleadings). */
  onAnnotatorPdfReady(): void {
    if (!this.isSyncEnabled || !this.activeShare || this.pendingSyncPage === null) {
      return;
    }
    const docId = Number(this.activeShare.document_index_id);
    const pageIdx = this.pendingSyncPage;
    const key = `${docId}:${pageIdx}`;
    setTimeout(() => {
      if (this.pendingSyncPage !== pageIdx) {
        return;
      }
      this.flushPendingSyncScroll(key);
    }, 0);
  }

  private flushPendingSyncScroll(appliedKey: string): void {
    if (this.pendingSyncPage === null || !this.annotator) {
      return;
    }
    if (this.annotator.pages.length === 0) {
      return;
    }
    const idx = this.pendingSyncPage;
    this.annotator.scrollToPage(idx);
    this.lastAppliedSyncKey = appliedKey;
    this.pendingSyncPage = null;
  }

  concludeHearing() {
    this.router.navigate(["/judges/dashboard/courtview"]);
  }

   formatVs(text: string): SafeHtml {
  if (!text) return '';

  // Step 1: Title case
  let formatted = text
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase());

  // Step 2: Replace vs
  formatted = formatted.replace(
    /\bVs\.?\s*/g,
    '<span class="vs-circle">vs</span> ',
  );

  return this.sanitizer.bypassSecurityTrustHtml(formatted);
}

  private loadCaseSummary(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.isLoading = true;
    this.loadError = "";

    this.courtroomService
      .getCaseSummary(this.efilingId, this.forwardedForDate)
      .subscribe({
        next: (resp) => {
          this.caseSummary = resp ?? null;
          this.orderEntries = Array.isArray(resp?.orders) ? resp.orders : [];
          this.forwardedForDate =
            resp?.forwarded_for_date ?? this.forwardedForDate;
          this.loadCaseDocuments();
          this.isLoading = false;
        },
        error: (err) => {
          console.warn("Failed to load case summary", err);
          this.loadError = err?.error?.detail || "Failed to load case details.";
          this.isLoading = false;
        },
      });
  }

  private loadCaseDocuments(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.courtroomService
      .getCaseDocuments(this.efilingId, this.forwardedForDate, null, false)
      .subscribe({
        next: (resp) => {
          this.allCaseDocuments = resp?.items ?? [];
          if (!this.orderEntries.length) {
            this.orderEntries = Array.isArray(resp?.orders) ? resp.orders : [];
          }
          if (this.allCaseDocuments.length && !this.previewDocument) {
            this.selectPreviewDocument(this.allCaseDocuments[0]);
          }
        },
        error: (err) => {
          console.warn("Failed to load case documents", err);
          this.allCaseDocuments = [];
        },
      });
  }

  selectPreviewDocument(doc: any, fromSync = false): void {
    if (!fromSync && this.isSyncEnabled) {
      this.isSyncEnabled = false;
      this.originalState = null;
      this.pendingSyncPage = null;
      this.lastAppliedSyncKey = null;
    }
    this.previewDocument = doc;
    this.updatePreviewUrl(doc ?? null);
  }

  private updatePreviewUrl(document: any | null): void {
    if (this.previewDocumentBlobUrl) {
      URL.revokeObjectURL(this.previewDocumentBlobUrl);
      this.previewDocumentBlobUrl = null;
    }
    const docId = Number(document?.id || 0);
    const fileUrl = document?.file_url || document?.file_part_path || null;
    if (!docId && !fileUrl) {
      this.previewLoadError = "";
      return;
    }
    const resolvedUrl = fileUrl
      ? this.courtroomService.resolveDocumentUrl(fileUrl)
      : "";
    this.previewLoadError = "";

    const stream$ = docId
      ? this.courtroomService.fetchDocumentBlobByIndex(docId)
      : this.courtroomService.fetchDocumentBlob(resolvedUrl);

    stream$.subscribe({
      next: (blob) => {
        this.previewDocumentBlobUrl = URL.createObjectURL(blob);
      },
      error: () => {
        this.previewLoadError =
          "Unable to load PDF preview (file missing or moved).";
      },
    });
  }

  onSaveAnnotations(payload: any) {
    if (!this.previewDocument || !this.canWrite) return;
    this.courtroomService
      .saveDocumentAnnotation({
        efiling_document_index_id: this.previewDocument.id,
        annotation_data: payload,
      })
      .subscribe({
        next: (res) => {
          this.previewDocument.annotation_data = res.annotation_data;
          Swal.fire({
            title: "Saved",
            icon: "success",
            timer: 1200,
            showConfirmButton: false,
            toast: true,
            position: "top-end",
          });
        },
        error: () => {
          Swal.fire({
            title: "Error",
            text: "Failed to save annotations.",
            icon: "error",
          });
        },
      });
  }

  get filteredCaseDocuments(): any[] {
    return orderDocumentsForDisplay(this.allCaseDocuments, this.documentSearchQuery);
  }

  get documentDisplaySections(): DocumentDisplaySection[] {
    return buildCollapsedDisplaySections(this.filteredCaseDocuments);
  }

  isVakalatGroupExpanded(id: string): boolean {
    return this.expandedVakalatGroupIds.has(id);
  }

  toggleVakalatGroup(id: string): void {
    if (this.expandedVakalatGroupIds.has(id)) {
      this.expandedVakalatGroupIds.delete(id);
      return;
    }
    this.expandedVakalatGroupIds.add(id);
  }

  private isPetitioner(value: any): boolean {
    return value === true || value === 1 || value === "1" || value === "true";
  }

  private toSequence(value: any): number | null {
    const n = Number(value);
    return Number.isFinite(n) && n > 0 ? n : null;
  }

  get petitionerLitigants(): any[] {
    const list = Array.isArray(this.caseSummary?.litigants)
      ? this.caseSummary.litigants
      : [];
    return list.filter((item: any) => this.isPetitioner(item?.is_petitioner));
  }

  get respondentLitigants(): any[] {
    const list = Array.isArray(this.caseSummary?.litigants)
      ? this.caseSummary.litigants
      : [];
    return list.filter((item: any) => !this.isPetitioner(item?.is_petitioner));
  }

  private normalizeLitigants(list: any[], side: "petitioner" | "respondent"): any[] {
    const safeList = Array.isArray(list) ? list : [];
    return safeList
      .map((item: any) => {
        const name = String(item?.name ?? "").trim();
        return {
          id: Number(item?.id || 0),
          name,
          sequence: this.toSequence(item?.sequence_number),
          roleLabel: side === "petitioner" ? "Petitioner" : "Respondent",
        };
      })
      .filter((item: any) => !!item.name)
      .sort((a: any, b: any) => {
        if (a.sequence === null && b.sequence === null) return 0;
        if (a.sequence === null) return 1;
        if (b.sequence === null) return -1;
        return a.sequence - b.sequence;
      });
  }

  private escapeHtml(value: string): string {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  private litigantsSectionHtml(title: string, rows: any[]): string {
    if (!rows.length) {
      return `
        <section class="litigants-modal__section">
          <h4 class="litigants-modal__heading">${title} (0)</h4>
          <div class="litigants-modal__empty">No entries available.</div>
        </section>
      `;
    }

    const items = rows
      .map(
        (row: any) => `
          <li class="litigants-modal__row">
            <span class="litigants-modal__name">${this.escapeHtml(row.name)}</span>
            <span class="litigants-modal__meta">${row.roleLabel}${row.sequence ? ` \u2022 Seq ${row.sequence}` : ""}</span>
          </li>
        `,
      )
      .join("");

    return `
      <section class="litigants-modal__section">
        <h4 class="litigants-modal__heading">${title} (${rows.length})</h4>
        <ul class="litigants-modal__list">${items}</ul>
      </section>
    `;
  }

  openLitigantsModal(): void {
    const caseNumber = this.caseSummary?.case_number || "Unnumbered case";
    const petitioners = this.normalizeLitigants(
      this.petitionerLitigants,
      "petitioner",
    );
    const respondents = this.normalizeLitigants(
      this.respondentLitigants,
      "respondent",
    );
    const total = petitioners.length + respondents.length;

    Swal.fire({
      title: `Litigants for Case ${caseNumber}`,
      html: `
        <div class="litigants-modal">
          <p class="litigants-modal__subtitle">Total parties: ${total}</p>
          ${this.litigantsSectionHtml("Petitioners", petitioners)}
          ${this.litigantsSectionHtml("Respondents", respondents)}
        </div>
      `,
      width: 760,
      confirmButtonText: "Close",
      customClass: {
        popup: "litigants-modal-popup",
      },
    });
  }

  get petitionerNamesLabel(): string {
    if (this.caseSummary?.petitioner_name)
      return this.caseSummary.petitioner_name;
    const parts = (this.caseSummary?.petitioner_vs_respondent || "").split(
      /v\/s/i,
    );
    return (parts[0] || "").trim() || "Petitioner";
  }

  get respondentNamesLabel(): string {
    if (this.caseSummary?.respondent_name)
      return this.caseSummary.respondent_name;
    const parts = (this.caseSummary?.petitioner_vs_respondent || "").split(
      /v\/s/i,
    );
    return parts.length > 1 ? (parts[1] || "").trim() : "Respondent";
  }

  openOrderFile(url: string | null | undefined): void {
    if (!url) return;
    window.open(url, "_blank", "noopener,noreferrer");
  }
}
