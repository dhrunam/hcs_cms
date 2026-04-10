import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DomSanitizer, SafeResourceUrl } from "@angular/platform-browser";
import { ActivatedRoute, Router, RouterLink } from "@angular/router";
import { forkJoin } from "rxjs";
import Swal from "sweetalert2";

import { EfilingService } from "../../../../services/advocate/efiling/efiling.services";
import {
  BenchConfiguration,
  ReaderService,
  resolveBenchConfiguration,
} from "../../../../services/reader/reader.service";
import { formatPetitionerVsRespondent } from "../../../../utils/petitioner-vs-respondent";

type Filing = any;
type CaseDetails = any;
type Litigant = any;
type FilingDoc = any;

@Component({
  selector: "app-listing-case-summary",
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: "./case-summary.html",
  styleUrl: "./case-summary.css",
})
export class ReaderCaseSummaryPage {
  isLoading = false;
  isSaving = false;
  loadError = "";
  filingId: number | null = null;
  filing: Filing | null = null;
  caseDetails: CaseDetails | null = null;
  litigants: Litigant[] = [];
  documents: FilingDoc[] = [];
  selectedDocument: FilingDoc | null = null;
  selectedDocumentUrl: SafeResourceUrl | null = null;
  selectedDocumentBlobUrl: string | null = null;
  requestedDocumentIndexIds: number[] = [];
  listingSummary = "";
  isForwarding = false;
  approvalStatus:
    | "NOT_FORWARDED"
    | "PENDING"
    | "APPROVED"
    | "REJECTED"
    | "REQUESTED_DOCS" = "NOT_FORWARDED";
  approvalNotes: string[] = [];
  approvalListingDate: string | null = null;
  canAssignListingDate = true;
  targetListingDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 10);
  approvalForwardedForDate: string | null = null;
  benchConfigurations: BenchConfiguration[] = [];
  listingRemark = "";

  constructor(
    private route: ActivatedRoute,
    private efilingService: EfilingService,
    private readerService: ReaderService,
    private sanitizer: DomSanitizer,
    private router: Router,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get("id"));
    this.filingId = Number.isFinite(id) ? id : null;
    if (!this.filingId) {
      this.loadError = "Missing filing id.";
      return;
    }
    this.load();
  }

  private load(): void {
    if (!this.filingId) return;
    this.isLoading = true;
    this.loadError = "";

    forkJoin({
      benchConfigurations: this.readerService.getBenchConfigurations({
        accessible_only: true,
      }),
      filing: this.efilingService.get_filing_by_id(this.filingId),
      caseDetails: this.efilingService.get_case_details_by_filing_id(
        this.filingId,
      ),
      litigants: this.efilingService.get_litigant_list_by_filing_id(
        this.filingId,
      ),
      documents: this.efilingService.get_document_reviews_by_filing_id(
        this.filingId,
        false,
      ),
      iaDocuments: this.efilingService.get_document_reviews_by_filing_id(
        this.filingId,
        true,
      ),
      registeredCases: this.readerService.getRegisteredCases({
        page_size: 500,
      }),
    }).subscribe({
      next: ({
        benchConfigurations,
        filing,
        caseDetails,
        litigants,
        documents,
        iaDocuments,
        registeredCases,
      }) => {
        this.benchConfigurations = benchConfigurations?.items ?? [];
        this.filing = filing;
        this.caseDetails = Array.isArray(caseDetails?.results)
          ? (caseDetails.results[0] ?? null)
          : Array.isArray(caseDetails)
            ? (caseDetails[0] ?? null)
            : null;
        this.litigants = Array.isArray(litigants?.results)
          ? litigants.results
          : Array.isArray(litigants)
            ? litigants
            : [];
        const mainDocs = Array.isArray(documents?.results)
          ? documents.results
          : Array.isArray(documents)
            ? documents
            : [];
        const iaDocs = Array.isArray(iaDocuments?.results)
          ? iaDocuments.results
          : Array.isArray(iaDocuments)
            ? iaDocuments
            : [];
        this.documents = [...mainDocs, ...iaDocs];
        this.selectedDocument = this.documents[0] ?? null;
        this.updatePreviewUrl(this.selectedDocument ?? null);

        const currentCase = (registeredCases?.items ?? []).find(
          (item: any) => Number(item?.efiling_id) === Number(this.filingId),
        );
        this.approvalStatus = (currentCase?.approval_status ??
          "NOT_FORWARDED") as any;
        this.approvalNotes = Array.isArray(currentCase?.approval_notes)
          ? currentCase.approval_notes
          : [];
        this.approvalListingDate = currentCase?.approval_listing_date || null;
        this.canAssignListingDate = currentCase?.can_assign_listing_date !== false;
        this.approvalForwardedForDate =
          currentCase?.approval_forwarded_for_date || null;
        if (this.approvalListingDate) {
          this.targetListingDate = this.approvalListingDate;
        }

        const requestedIds = Array.isArray(currentCase?.requested_documents)
          ? currentCase.requested_documents
              .map((item: any) => Number(item?.document_index_id))
              .filter((item: number) => Number.isFinite(item))
          : [];
        this.requestedDocumentIndexIds = requestedIds;
        this.listingSummary = (currentCase?.listing_summary || "").trim();
        this.isLoading = false;
      },
      error: (err) => {
        console.warn("Failed to load case summary", err);
        this.loadError = "Failed to load case summary.";
        this.isLoading = false;
      },
    });
  }

  documentName(document: any): string {
    return (
      document?.document_part_name ||
      document?.description ||
      document?.document_name ||
      document?.name ||
      document?.file_name ||
      "Document"
    );
  }

  selectDocument(document: any): void {
    this.selectedDocument = document;
    this.updatePreviewUrl(document ?? null);
  }

  isSelectedDocument(docId: number): boolean {
    return Number(this.selectedDocument?.id) === Number(docId);
  }

  isRequestedDocument(docId: number): boolean {
    return this.requestedDocumentIndexIds.includes(docId);
  }

  get forwardDocumentIndexIds(): number[] {
    return Array.from(
      new Set(
        this.documents
          .map((document) => Number(document?.id))
          .filter(
            (documentId) => Number.isFinite(documentId) && documentId > 0,
          ),
      ),
    );
  }

  private updatePreviewUrl(document: any | null): void {
    if (this.selectedDocumentBlobUrl) {
      URL.revokeObjectURL(this.selectedDocumentBlobUrl);
      this.selectedDocumentBlobUrl = null;
    }
    const docId = Number(document?.id || 0);
    const fileUrl = document?.file_url ?? null;
    if (!docId && !fileUrl) {
      this.selectedDocumentUrl = null;
      return;
    }
    if (fileUrl) {
      this.selectedDocumentUrl =
        this.sanitizer.bypassSecurityTrustResourceUrl(fileUrl);
    }
    const stream$ = docId
      ? this.efilingService.fetch_document_blob_by_index(docId)
      : this.efilingService.fetch_document_blob(fileUrl);
    stream$.subscribe({
      next: (blob) => {
        this.selectedDocumentBlobUrl = URL.createObjectURL(blob);
        this.selectedDocumentUrl =
          this.sanitizer.bypassSecurityTrustResourceUrl(
            this.selectedDocumentBlobUrl,
          );
      },
      error: () => {
        if (fileUrl) {
          this.selectedDocumentUrl =
            this.sanitizer.bypassSecurityTrustResourceUrl(fileUrl);
        } else {
          this.selectedDocumentUrl = null;
        }
      },
    });
  }

  get forwardBenchConfiguration(): BenchConfiguration | undefined {
    return this.benchConfigurations.find((item) => item.is_forward_target);
  }

  forwardToJudge(): void {
    if (!this.filingId || !this.forwardBenchConfiguration) return;
    const summary = (this.listingSummary || "").trim();
    if (!summary) {
      Swal.fire({
        title: "Summary Required",
        text: "Please write case summary before forwarding.",
        icon: "warning",
      });
      return;
    }
    this.isForwarding = true;
    const today = new Date().toISOString().slice(0, 10);
    this.readerService
      .forwardToCourtroom({
        forwarded_for_date: today,
        bench_key: this.forwardBenchConfiguration.bench_key,
        listing_summary: summary,
        document_index_ids: this.forwardDocumentIndexIds.length
          ? this.forwardDocumentIndexIds
          : undefined,
        efiling_ids: [this.filingId],
      })
      .subscribe({
        next: () => {
          this.isForwarding = false;
          this.approvalStatus = "PENDING";
          this.approvalForwardedForDate = today;
          Swal.fire({
            title: "Forwarded",
            text: "Case forwarded to your mapped judge for review.",
            icon: "success",
            timer: 1300,
            showConfirmButton: false,
          });
          this.router.navigate(['/reader/dashboard/registered-cases'])
        },
        error: (err) => {
          console.warn("forwardToJudge failed", err);
          this.isForwarding = false;
          Swal.fire({
            title: "Forward Failed",
            text: err?.error?.detail || "Unable to forward request.",
            icon: "error",
          });
        },
      });
  }

  get petitionerVsRespondentLine(): string {
    const fromApi = String(this.filing?.petitioner_vs_respondent || '').trim();
    if (fromApi) return fromApi;
    const computed = formatPetitionerVsRespondent(
      this.litigants,
      String(this.filing?.petitioner_name || ''),
    );
    return computed || '—';
  }

  get petitionerName(): string {
    const petitioner = this.litigants.find(
      (litigant: any) => litigant?.is_petitioner === true,
    );
    return petitioner?.name || this.filing?.petitioner_name || "-";
  }

  get respondentName(): string {
    const respondent = this.litigants.find(
      (litigant: any) => litigant?.is_petitioner === false,
    );
    return respondent?.name || "-";
  }

  benchLabel(key: string | null | undefined): string {
    if (this.isUnassignedBench(key)) return "-";
    const normalizedKey = String(key ?? "").trim();
    return (
      resolveBenchConfiguration(this.benchConfigurations, normalizedKey)
        ?.label || normalizedKey
    );
  }

  private isUnassignedBench(key: string | null | undefined): boolean {
    const value = String(key ?? "").trim().toLowerCase();
    return (
      !value ||
      value === "high court of sikkim" ||
      value === "high court of skkim"
    );
  }

  get canSendBackToScrutiny(): boolean {
    return (
      !this.approvalListingDate && !this.isUnassignedBench(this.filing?.bench)
    );
  }

  forwardForListing(): void {
    if (
      !this.filingId ||
      !this.canAssignListingDate ||
      !this.targetListingDate ||
      !this.approvalForwardedForDate
    ) {
      return;
    }
    this.isSaving = true;
    this.readerService
      .assignDate({
        efiling_ids: [this.filingId],
        listing_date: this.targetListingDate,
        forwarded_for_date: this.approvalForwardedForDate,
        listing_remark: this.listingRemark,
      })
      .subscribe({
        next: () => {
          this.isSaving = false;
          this.approvalListingDate = this.targetListingDate;
          Swal.fire({
            title: "Forwarded for Listing",
            text: `Case has been assigned listing date ${this.targetListingDate} and forwarded to Listing Officer.`,
            icon: "success",
            timer: 2000,
            showConfirmButton: false,
          });
        },
        error: (err) => {
          console.warn("forwardForListing failed", err);
          this.isSaving = false;
          Swal.fire({
            title: "Error",
            text: "Failed to assign date.",
            icon: "error",
          });
        },
      });
  }

  sendBackToScrutiny(): void {
    if (!this.filingId) return;
    Swal.fire({
      title: "Send back to Scrutiny?",
      text: "This will reset the bench and send the case back to the Scrutiny pool for re-assignment.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, Send Back",
      confirmButtonColor: "#d33",
    }).then((result) => {
      if (result.isConfirmed) {
        this.isSaving = true;
        this.readerService.resetBench(this.filingId!).subscribe({
          next: () => {
            this.isSaving = false;
            Swal.fire({
              title: "Returned",
              text: "Case returned to Scrutiny pool.",
              icon: "success",
              timer: 1500,
              showConfirmButton: false,
            });
            this.router.navigate(["/reader/dashboard/registered-cases"]);
          },
          error: (err) => {
            this.isSaving = false;
            console.warn("resetBench failed", err);
            Swal.fire({
              title: "Error",
              text: "Failed to reset bench.",
              icon: "error",
            });
          },
        });
      }
    });
  }

  get formattedListingDate(): string {
    if (!this.targetListingDate) return "";
    const date = new Date(this.targetListingDate);
    const day = date.getDate();
    const month = date.toLocaleString("default", { month: "long" });
    const year = date.getFullYear();
    const suffix = (value: number) => {
      if (value > 3 && value < 21) return "th";
      switch (value % 10) {
        case 1:
          return "st";
        case 2:
          return "nd";
        case 3:
          return "rd";
        default:
          return "th";
      }
    };
    return `${day}${suffix(day)} ${month} ${year}`;
  }

  get showListingAuthorityNotice(): boolean {
    return (
      (this.approvalStatus === "APPROVED" || !!this.approvalListingDate) &&
      !this.canAssignListingDate &&
      !this.approvalListingDate
    );
  }
}
