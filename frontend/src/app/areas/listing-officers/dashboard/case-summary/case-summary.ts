import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import Swal from 'sweetalert2';

import { EfilingService } from '../../../../services/advocate/efiling/efiling.services';
import { CauseListService } from '../../../../services/listing/cause-list.service';
import { benchLabel, BENCH_LABELS, BenchKey, isUnassignedBench } from '../../shared/bench-labels';

type Filing = any;
type CaseDetails = any;
type Litigant = any;
type FilingDoc = any;

@Component({
  selector: 'app-listing-case-summary',
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './case-summary.html',
  styleUrl: './case-summary.css',
})
export class ListingCaseSummaryPage {
  isLoading = false;
  isSaving = false;
  loadError = '';

  filingId: number | null = null;

  filing: Filing | null = null;
  caseDetails: CaseDetails | null = null;
  litigants: Litigant[] = [];
  documents: FilingDoc[] = [];
  selectedDocument: FilingDoc | null = null;
  selectedDocumentUrl: SafeResourceUrl | null = null;
  selectedDocumentBlobUrl: string | null = null;
  selectedDocumentIndexIds: number[] = [];
  listingSummary = '';
  isForwarding = false;

  benchKeys: BenchKey[] = Object.keys(BENCH_LABELS) as BenchKey[];
  benchLabel = benchLabel;
  selectedBench: BenchKey | null = null;

  constructor(
    private route: ActivatedRoute,
    private efilingService: EfilingService,
    private causeListService: CauseListService,
    private sanitizer: DomSanitizer,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.filingId = Number.isFinite(id) ? id : null;
    if (!this.filingId) {
      this.loadError = 'Missing filing id.';
      return;
    }
    this.load();
  }

  private load(): void {
    if (!this.filingId) return;
    this.isLoading = true;
    this.loadError = '';

    forkJoin({
      filing: this.efilingService.get_filing_by_id(this.filingId),
      caseDetails: this.efilingService.get_case_details_by_filing_id(this.filingId),
      litigants: this.efilingService.get_litigant_list_by_filing_id(this.filingId),
      documents: this.efilingService.get_document_reviews_by_filing_id(this.filingId, false),
      iaDocuments: this.efilingService.get_document_reviews_by_filing_id(this.filingId, true),
      registeredCases: this.causeListService.getRegisteredCases({ page_size: 500 }),
    }).subscribe({
      next: ({ filing, caseDetails, litigants, documents, iaDocuments, registeredCases }) => {
        this.filing = filing;
        this.caseDetails = Array.isArray(caseDetails?.results)
          ? caseDetails.results[0] ?? null
          : Array.isArray(caseDetails)
            ? caseDetails[0] ?? null
            : null;
        this.litigants = Array.isArray(litigants?.results) ? litigants.results : Array.isArray(litigants) ? litigants : [];
        const mainDocs = Array.isArray(documents?.results) ? documents.results : Array.isArray(documents) ? documents : [];
        const iaDocs = Array.isArray(iaDocuments?.results) ? iaDocuments.results : Array.isArray(iaDocuments) ? iaDocuments : [];
        this.documents = [...mainDocs, ...iaDocs];
        this.selectedDocument = this.documents[0] ?? null;
        this.updatePreviewUrl(this.selectedDocument?.file_url ?? null);
        const currentCase = (registeredCases?.items ?? []).find((x: any) => Number(x?.efiling_id) === Number(this.filingId));
        const requestedIds = Array.isArray(currentCase?.requested_documents)
          ? currentCase.requested_documents
              .map((x: any) => Number(x?.document_index_id))
              .filter((x: number) => Number.isFinite(x))
          : [];
        this.selectedDocumentIndexIds = requestedIds.length
          ? requestedIds
          : (this.selectedDocument?.id ? [this.selectedDocument.id] : []);
        this.listingSummary = (currentCase?.listing_summary || '').trim();

        const existingBench = (this.filing?.bench as string | null) ?? null;
        this.selectedBench = (!isUnassignedBench(existingBench) && this.benchKeys.includes(existingBench as BenchKey)
          ? (existingBench as BenchKey)
          : this.benchKeys[0]) ?? null;

        this.isLoading = false;
      },
      error: (err) => {
        console.warn('Failed to load case summary', err);
        this.loadError = 'Failed to load case summary.';
        this.isLoading = false;
      },
    });
  }

  documentName(d: any): string {
    return d?.document_part_name || d?.description || d?.document_name || d?.name || d?.file_name || 'Document';
  }

  documentUrl(d: any): string | null {
    return d?.file_url || d?.document || d?.file || null;
  }

  selectDocument(d: any): void {
    this.selectedDocument = d;
    this.updatePreviewUrl(d?.file_url ?? null);
  }

  isDocSelected(docId: number): boolean {
    return this.selectedDocumentIndexIds.includes(docId);
  }

  toggleDocSelection(docId: number, checked: boolean): void {
    if (checked) {
      if (!this.selectedDocumentIndexIds.includes(docId)) {
        this.selectedDocumentIndexIds = [...this.selectedDocumentIndexIds, docId];
      }
      return;
    }
    this.selectedDocumentIndexIds = this.selectedDocumentIndexIds.filter((id) => id !== docId);
  }

  private updatePreviewUrl(fileUrl: string | null): void {
    if (this.selectedDocumentBlobUrl) {
      URL.revokeObjectURL(this.selectedDocumentBlobUrl);
      this.selectedDocumentBlobUrl = null;
    }
    if (!fileUrl) {
      this.selectedDocumentUrl = null;
      return;
    }
    this.selectedDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(fileUrl);
    this.efilingService.fetch_document_blob(fileUrl).subscribe({
      next: (blob) => {
        this.selectedDocumentBlobUrl = URL.createObjectURL(blob);
        this.selectedDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.selectedDocumentBlobUrl);
      },
      error: () => {
        this.selectedDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(fileUrl);
      },
    });
  }

  forwardToJudge(): void {
    if (!this.filingId || !this.selectedBench) return;
    const summary = (this.listingSummary || '').trim();
    if (!summary) {
      Swal.fire({ title: 'Summary Required', text: 'Please write case summary before forwarding.', icon: 'warning' });
      return;
    }
    if (!this.selectedDocumentIndexIds.length) {
      Swal.fire({ title: 'Select Documents', text: 'Select at least one document to forward.', icon: 'warning' });
      return;
    }
    this.isForwarding = true;
    const today = new Date().toISOString().slice(0, 10);
    this.causeListService.forwardToCourtroom({
      forwarded_for_date: today,
      bench_key: this.selectedBench,
      listing_summary: summary,
      document_index_ids: this.selectedDocumentIndexIds,
      efiling_ids: [this.filingId],
    }).subscribe({
      next: () => {
        this.isForwarding = false;
        Swal.fire({
          title: 'Forwarded',
          text: 'Request forwarded to judge(s).',
          icon: 'success',
          timer: 1200,
          showConfirmButton: false,
        });
      },
      error: (err) => {
        console.warn('forwardToJudge failed', err);
        this.isForwarding = false;
        Swal.fire({ title: 'Forward Failed', text: err?.error?.detail || 'Unable to forward request.', icon: 'error' });
      },
    });
  }

  get petitionerName(): string {
    const pet = this.litigants.find((l: any) => l?.is_petitioner === true);
    return pet?.name || this.filing?.petitioner_name || '-';
  }

  get respondentName(): string {
    const res = this.litigants.find((l: any) => l?.is_petitioner === false);
    return res?.name || '-';
  }

  get isBenchLocked(): boolean {
    return !isUnassignedBench(this.filing?.bench);
  }

  saveBench(): void {
    if (!this.filingId || !this.selectedBench || this.isBenchLocked) return;
    this.isSaving = true;
    this.causeListService
      .assignBenches([{ efiling_id: this.filingId, bench_key: this.selectedBench }])
      .subscribe({
        next: () => {
          if (this.filing) this.filing.bench = this.selectedBench;
          this.isSaving = false;
        },
        error: (err) => {
          console.warn('Failed to assign bench', err);
          this.isSaving = false;
        },
      });
  }
}

