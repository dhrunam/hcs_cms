import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DomSanitizer, SafeResourceUrl, SafeHtml } from "@angular/platform-browser";
import { ActivatedRoute, Router, RouterLink } from "@angular/router";
import Swal from "sweetalert2";

import { AuthService } from "../../../../auth.service";
import { CourtroomService } from "../../../../services/judge/courtroom.service";
import { benchLabel } from "../../../listing-officers/shared/bench-labels";
import { PdfAnnotatorComponent } from "./pdf-annotator.component";

@Component({
  selector: "app-judge-courtroom",
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: "./courtroom.html",
  styleUrl: "./courtroom.css",
})
export class JudgeCourtroomPage {
  benchLabel = benchLabel;
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

  private readCanWrite(): boolean {
    const groups = this.auth.getUserGroups();
    return groups.some((g) =>
      ["API_JUDGE", "JUDGE_CJ", "JUDGE_J1", "JUDGE_J2"].includes(String(g)),
    );
  }

  private loadCaseSummary(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.isLoading = true;
    this.loadError = "";

    this.courtroomService
      .getCaseSummary(this.efilingId, this.forwardedForDate, this.forwardBenchKey)
      .subscribe({
        next: (resp) => {
          this.caseSummary = resp ?? null;
          this.forwardedForDate =
            resp?.forwarded_for_date ?? this.forwardedForDate;
          this.forwardBenchKey =
            resp?.forward_bench_key ?? this.forwardBenchKey;
          this.decisionNotes = resp?.judge_decision?.decision_notes ?? "";
          this.loadCaseDocuments();
          this.isLoading = false;

          console.log("Case Summary Is", this.caseSummary);
        },
        error: (err) => {
          console.warn("Failed to load courtroom case summary", err);
          this.loadError = "Failed to load case details.";
          this.isLoading = false;
        },
      });
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
          this.allCaseDocuments = resp?.items ?? [];
          if (this.allCaseDocuments.length && !this.previewDocument) {
            this.selectPreviewDocument(this.allCaseDocuments[0]);
          }
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
    const q = this.docSearch.trim().toLowerCase();
    if (!q) return this.allCaseDocuments;
    return this.allCaseDocuments.filter((d) => {
      const name = String(
        d?.document_part_name || d?.document_type || "",
      ).toLowerCase();
      return name.includes(q);
    });
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
