import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DomSanitizer, SafeResourceUrl, SafeHtml } from "@angular/platform-browser";
import { ActivatedRoute, Router, RouterLink } from "@angular/router";
import { catchError, forkJoin, of } from "rxjs";
import Swal from "sweetalert2";

import { AuthService } from "../../../../auth.service";
import { CourtroomService } from "../../../../services/judge/courtroom.service";
import { benchLabel } from "../../../listing-officers/shared/bench-labels";
import { OfficeNoteEditor } from "../../../office-note-sheet/note-editor/note-editor";
import { buildCollapsedDisplaySections, DocumentDisplaySection, orderDocumentsForDisplay } from "../../../../shared/document-groups";

@Component({
  selector: "app-judge-courtroom",
  imports: [CommonModule, FormsModule, RouterLink, OfficeNoteEditor],
  templateUrl: "./courtroom.html",
  styleUrl: "./courtroom.css",
})
export class JudgeCourtroomPage {
  benchLabel = benchLabel;
  activeTab: 'details' | 'notes' = 'details';
  efilingId: number | null = null;
  forwardedForDate: string | null = null;
  forwardBenchKey: string | null = null;

  isLoading = false;
  loadError = "";
  documentsLoadError = "";

  caseSummary: any = null;
  decisionNotes = "";
  allCaseDocuments: any[] = [];
  docSearch = "";
  previewDocument: any = null;
  previewDocumentUrl: SafeResourceUrl | null = null;
  previewDocumentBlobUrl: string | null = null;
  previewLoadError = "";

  canWrite = false;
  private expandedVakalatGroupIds = new Set<string>();
  private expandedOrdersGroupIds = new Set<string>();

  constructor(
    private route: ActivatedRoute,
    private courtroomService: CourtroomService,
    private sanitizer: DomSanitizer,
    private router: Router,
    private auth: AuthService,
  ) {}

  ngOnInit(): void {
    this.canWrite = this.readCanWrite();

    const idRaw = this.route.snapshot.paramMap.get("id");
    this.efilingId = idRaw ? Number(idRaw) : null;

    this.forwardedForDate =
      this.route.snapshot.queryParamMap.get("forwarded_for_date");
    this.forwardBenchKey =
      this.route.snapshot.queryParamMap.get("forward_bench_key");
    if (!this.efilingId || !this.forwardedForDate) {
      this.loadError = "Missing case id or forwarded_for_date.";
      return;
    }

    this.loadCaseSummary();
  }

  setActiveTab(tab: 'details' | 'notes'): void {
    this.activeTab = tab;
  }

  private readCanWrite(): boolean {
    const groups = this.auth.getUserGroups();
    return groups.some((g) =>
      ["JUDGE", "JUDGE_CJ", "JUDGE_J1", "JUDGE_J2"].includes(String(g)),
    );
  }

  private loadCaseSummary(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.isLoading = true;
    this.loadError = "";

    const benchForParallel = this.forwardBenchKey;
    forkJoin({
      summary: this.courtroomService.getCaseSummary(
        this.efilingId,
        this.forwardedForDate,
        benchForParallel,
      ),
      documents: this.courtroomService
        .getCaseDocuments(
          this.efilingId,
          this.forwardedForDate,
          benchForParallel,
          false,
        )
        .pipe(
          catchError((err) => {
            console.warn("Courtroom documents parallel load failed", err);
            return of({ items: [] as any[] });
          }),
        ),
    }).subscribe({
      next: ({ summary, documents }) => {
        this.caseSummary = summary ?? null;
        this.forwardedForDate =
          summary?.forwarded_for_date ?? this.forwardedForDate;
        const resolvedBench =
          summary?.forward_bench_key ?? this.forwardBenchKey;
        this.decisionNotes = summary?.judge_decision?.decision_notes ?? "";
        const benchChanged =
          String(resolvedBench ?? "") !== String(benchForParallel ?? "");
        this.forwardBenchKey = resolvedBench;
        if (benchChanged) {
          this.loadCaseDocuments();
        } else {
          this.applyDocumentsResponse(documents);
        }
        this.isLoading = false;
      },
      error: (err) => {
        console.warn("Failed to load courtroom case summary", err);
        this.loadError = "Failed to load case details.";
        this.isLoading = false;
      },
    });
  }

  private applyDocumentsResponse(resp: { items?: any[] } | null): void {
    this.allCaseDocuments = resp?.items ?? [];
    if (this.allCaseDocuments.length && !this.previewDocument) {
      this.selectPreviewDocument(this.allCaseDocuments[0]);
    }
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

  submitDecision(): void {
    if (!this.canWrite || !this.efilingId || !this.forwardedForDate) return;

    Swal.fire({
      title: "Save decision?",
      text: "This will save the judge remarks and send the case to the reader.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, save",
    }).then((res) => {
      if (!res.isConfirmed) return;

      this.courtroomService
        .saveDecision({
          efiling_id: this.efilingId!,
          forwarded_for_date: this.forwardedForDate!,
          forward_bench_key: this.caseSummary?.forward_bench_key || undefined,
          decision_notes: this.decisionNotes || null,
        })
        .subscribe({
          next: () => {
            Swal.fire({
              title: "Saved",
              text: "Decision saved and sent to reader.",
              icon: "success",
              timer: 1000,
              showConfirmButton: false,
            });
            this.router.navigate(["/judges/dashboard/home"], {
              queryParams: { forwarded_for_date: this.forwardedForDate },
            });
          },
          error: (err) => {
            console.warn("save decision failed", err);
            Swal.fire({
              title: "Error",
              text: "Failed to save decision.",
              icon: "error",
            });
          },
        });
    });
  }

  private loadCaseDocuments(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.documentsLoadError = "";
    this.courtroomService
      .getCaseDocuments(this.efilingId, this.forwardedForDate, this.forwardBenchKey, false)
      .subscribe({
        next: (resp) => {
          this.applyDocumentsResponse(resp);
        },
        error: (err) => {
          console.warn("Failed to load case documents", err);
          this.allCaseDocuments = [];
          const msg =
            err?.error?.detail ||
            err?.error?.message ||
            (typeof err?.error === "string" ? err.error : null);
          this.documentsLoadError =
            msg || "Could not load case documents (check login or network).";
        },
      });
  }

  get filteredDocuments(): any[] {
    return orderDocumentsForDisplay(this.allCaseDocuments, this.docSearch);
  }

  get documentDisplaySections(): DocumentDisplaySection[] {
    return buildCollapsedDisplaySections(this.filteredDocuments);
  }

  publishedOrderLabel(doc: any): string | null {
    const raw = doc?.published_order_at;
    if (!raw) return null;
    try {
      const d = new Date(raw);
      if (Number.isNaN(d.getTime())) return null;
      return `Published: ${d.toLocaleString()}`;
    } catch {
      return null;
    }
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

  isOrdersGroupExpanded(id: string): boolean {
    return this.expandedOrdersGroupIds.has(id);
  }

  toggleOrdersGroup(id: string): void {
    if (this.expandedOrdersGroupIds.has(id)) {
      this.expandedOrdersGroupIds.delete(id);
      return;
    }
    this.expandedOrdersGroupIds.add(id);
  }

  selectPreviewDocument(doc: any): void {
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
      this.previewDocumentUrl = null;
      this.previewLoadError = "";
      return;
    }
    const resolvedUrl = fileUrl
      ? this.courtroomService.resolveDocumentUrl(fileUrl)
      : "";
    if (fileUrl) {
      this.previewDocumentUrl =
        this.sanitizer.bypassSecurityTrustResourceUrl(resolvedUrl);
    }
    this.previewLoadError = "";
    const stream$ = docId
      ? this.courtroomService.fetchDocumentBlobByIndex(docId)
      : this.courtroomService.fetchDocumentBlob(resolvedUrl);
    stream$.subscribe({
      next: (blob) => {
        this.previewDocumentBlobUrl = URL.createObjectURL(blob);
        this.previewDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
          this.previewDocumentBlobUrl,
        );
      },
      error: () => {
        this.previewDocumentUrl = null;
        this.previewLoadError =
          "Unable to load this PDF preview (file missing or moved).";
      },
    });
  }

  private isPetitioner(value: any): boolean {
    return value === true || value === 1 || value === "1" || value === "true";
  }

  private toSequence(value: any): number | null {
    const n = Number(value);
    return Number.isFinite(n) && n > 0 ? n : null;
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

  private formatLitigantNames(list: any[]): string {
    const safeList = Array.isArray(list) ? list : [];
    const sorted = [...safeList].sort((a: any, b: any) => {
      const as = Number(a?.sequence_number ?? 0);
      const bs = Number(b?.sequence_number ?? 0);
      if (!as && !bs) return 0;
      if (!as) return 1;
      if (!bs) return -1;
      return as - bs;
    });

    const names = sorted
      .map((l: any) => String(l?.name ?? "").trim())
      .filter((n: string) => !!n);
    return names.length ? names.join(", ") : "-";
  }

  get petitionerNamesLabel(): string {
    return this.formatLitigantNames(this.petitionerLitigants);
  }

  get respondentNamesLabel(): string {
    return this.formatLitigantNames(this.respondentLitigants);
  }

}
