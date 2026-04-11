import { CommonModule } from "@angular/common";
import { Component, OnInit, OnDestroy, ViewChild } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ActivatedRoute, Router, RouterLink } from "@angular/router";
import Swal from "sweetalert2";

import { CourtroomService } from "../../../../services/judge/courtroom.service";
import { benchLabel } from "../../../listing-officers/shared/bench-labels";
import { PdfAnnotatorComponent } from "../courtroom/pdf-annotator.component";
import { DomSanitizer, SafeHtml } from "@angular/platform-browser";

@Component({
  selector: "app-judge-courtview-case",
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, PdfAnnotatorComponent],
  templateUrl: "./courtview-case.html",
  styleUrl: "./courtview-case.css",
})
export class JudgeCourtviewCasePage implements OnInit, OnDestroy {
  @ViewChild(PdfAnnotatorComponent) annotator?: PdfAnnotatorComponent;
  benchLabel = benchLabel;
  efilingId: number | null = null;
  forwardedForDate: string | null = null;

  isLoading = false;
  loadError = "";

  caseSummary: any = null;
  allCaseDocuments: any[] = [];

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
      .getCaseDocuments(this.efilingId, this.forwardedForDate, null ,false)
      .subscribe({
        next: (resp) => {
          this.allCaseDocuments = resp?.items ?? [];
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
    if (!this.documentSearchQuery.trim()) {
      return this.allCaseDocuments;
    }
    const q = this.documentSearchQuery.toLowerCase().trim();
    return this.allCaseDocuments.filter((doc, idx) => {
      const name = (doc.document_part_name || "").toLowerCase();
      const type = (doc.document_type || "").toLowerCase();
      const indexStr = String(idx + 1);
      return name.includes(q) || type.includes(q) || indexStr === q;
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
}
