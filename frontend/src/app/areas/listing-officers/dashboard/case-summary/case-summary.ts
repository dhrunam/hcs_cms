import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import Swal from 'sweetalert2';

import { EfilingService } from '../../../../services/advocate/efiling/efiling.services';
import {
  BenchConfiguration,
  CauseListService,
} from '../../../../services/listing/cause-list.service';
import { formatPetitionerVsRespondent } from '../../../../utils/petitioner-vs-respondent';
import {
  isPublishedCourtOrderDoc,
  orderDocumentsForDisplay,
  sortCourtOrdersNewestFirst,
} from '../../../../shared/document-groups';
import { OfficeNoteEditor } from '../../../office-note-sheet/note-editor/note-editor';

type Filing = any;
type CaseDetails = any;
type Litigant = any;
type FilingDoc = any;

@Component({
  selector: 'app-listing-case-summary',
  imports: [CommonModule, RouterLink, FormsModule, OfficeNoteEditor],
  templateUrl: './case-summary.html',
  styleUrl: './case-summary.css',
})
export class ListingCaseSummaryPage {
  activeTab: 'details' | 'notes' = 'details';
  isLoading = false;
  isSaving = false;
  loadError = '';

  filingId: number | null = null;

  filing: Filing | null = null;
  caseDetails: CaseDetails | null = null;
  litigants: Litigant[] = [];
  documents: FilingDoc[] = [];
  pleadingDocuments: FilingDoc[] = [];
  courtOrderDocuments: FilingDoc[] = [];
  selectedDocument: FilingDoc | null = null;
  selectedDocumentUrl: SafeResourceUrl | null = null;
  selectedDocumentBlobUrl: string | null = null;
  selectedDocumentIndexIds: number[] = [];
  listingSummary = '';
  isForwarding = false;
  approvalStatus: 'NOT_FORWARDED' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'REQUESTED_DOCS' = 'NOT_FORWARDED';
  approvalNotes: string[] = [];

  benchConfigurations: BenchConfiguration[] = [];
  selectedBench: string | null = null;

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

  setActiveTab(tab: 'details' | 'notes'): void {
    this.activeTab = tab;
  }

  private load(): void {
    if (!this.filingId) return;
    this.isLoading = true;
    this.loadError = '';

    forkJoin({
      benchConfigurations: this.causeListService.getBenchConfigurations(),
      filing: this.efilingService.get_filing_by_id(this.filingId),
      caseDetails: this.efilingService.get_case_details_by_filing_id(this.filingId),
      litigants: this.efilingService.get_litigant_list_by_filing_id(this.filingId),
      documents: this.efilingService.get_document_reviews_by_filing_id(this.filingId, false),
      iaDocuments: this.efilingService.get_document_reviews_by_filing_id(this.filingId, true),
      registeredCases: this.causeListService.getRegisteredCases({ page_size: 500 }),
    }).subscribe({
      next: ({ benchConfigurations, filing, caseDetails, litigants, documents, iaDocuments, registeredCases }) => {
        this.benchConfigurations = benchConfigurations?.items ?? [];
        this.filing = filing;
        this.caseDetails = Array.isArray(caseDetails?.results)
          ? caseDetails.results[0] ?? null
          : Array.isArray(caseDetails)
            ? caseDetails[0] ?? null
            : null;
        this.litigants = Array.isArray(litigants?.results) ? litigants.results : Array.isArray(litigants) ? litigants : [];
        const mainDocs = Array.isArray(documents?.results) ? documents.results : Array.isArray(documents) ? documents : [];
        const iaDocs = Array.isArray(iaDocuments?.results) ? iaDocuments.results : Array.isArray(iaDocuments) ? iaDocuments : [];
        this.documents = orderDocumentsForDisplay([...mainDocs, ...iaDocs], "");
        this.courtOrderDocuments = sortCourtOrdersNewestFirst(
          this.documents.filter((doc: any) => isPublishedCourtOrderDoc(doc)),
        );
        this.pleadingDocuments = this.documents.filter(
          (doc: any) => !isPublishedCourtOrderDoc(doc),
        );
        this.selectedDocument = this.documents[0] ?? null;
        this.updatePreviewUrl(this.selectedDocument ?? null);
        const currentCase = (registeredCases?.items ?? []).find((x: any) => Number(x?.efiling_id) === Number(this.filingId));
        this.approvalStatus = (currentCase?.approval_status ?? 'NOT_FORWARDED') as any;
        this.approvalNotes = Array.isArray(currentCase?.approval_notes) ? currentCase.approval_notes : [];
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
        const benchKeys = this.benchConfigurations.map((item) => item.bench_key);
        this.selectedBench = (!this.isUnassignedBench(existingBench) && benchKeys.includes(existingBench || ''))
          ? existingBench
          : (benchKeys[0] ?? null);

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

  publishedOrderLabel(d: any): string | null {
    const raw = d?.published_order_at;
    if (!raw) return null;
    try {
      const dt = new Date(raw);
      if (Number.isNaN(dt.getTime())) return null;
      return `Published: ${dt.toLocaleString()}`;
    } catch {
      return null;
    }
  }

  documentUrl(d: any): string | null {
    return d?.file_url || d?.document || d?.file || null;
  }

  selectDocument(d: any): void {
    this.selectedDocument = d;
    this.updatePreviewUrl(d ?? null);
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
      this.selectedDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(fileUrl);
    }
    const stream$ = docId
      ? this.efilingService.fetch_document_blob_by_index(docId)
      : this.efilingService.fetch_document_blob(fileUrl);
    stream$.subscribe({
      next: (blob) => {
        this.selectedDocumentBlobUrl = URL.createObjectURL(blob);
        this.selectedDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.selectedDocumentBlobUrl);
      },
      error: () => {
        if (fileUrl) {
          this.selectedDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(fileUrl);
        } else {
          this.selectedDocumentUrl = null;
        }
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
    this.isForwarding = true;
    const today = new Date().toISOString().slice(0, 10);
    // Ensure bench is persisted first so case appears in generator.
    this.causeListService.assignBenches([{ efiling_id: this.filingId, bench_key: this.selectedBench }]).subscribe({
      next: () => {
        if (this.filing) this.filing.bench = this.selectedBench;
        this.causeListService.forwardToCourtroom({
          forwarded_for_date: today,
          bench_key: this.selectedBench!,
          listing_summary: summary,
          document_index_ids: this.selectedDocumentIndexIds.length ? this.selectedDocumentIndexIds : undefined,
          efiling_ids: [this.filingId!],
        }).subscribe({
          next: () => {
            this.isForwarding = false;
            this.approvalStatus = 'PENDING';
            Swal.fire({
              title: 'Forwarded',
              text: 'Bench saved and case forwarded to judge(s).',
              icon: 'success',
              timer: 1300,
              showConfirmButton: false,
            });
          },
          error: (err) => {
            console.warn('forwardToJudge failed', err);
            this.isForwarding = false;
            Swal.fire({ title: 'Forward Failed', text: err?.error?.detail || 'Unable to forward request.', icon: 'error' });
          },
        });
      },
      error: (err) => {
        console.warn('assign before forward failed', err);
        this.isForwarding = false;
        Swal.fire({ title: 'Bench Save Failed', text: err?.error?.detail || 'Unable to save bench before forwarding.', icon: 'error' });
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
    const pet = this.litigants.find((l: any) => l?.is_petitioner === true);
    return pet?.name || this.filing?.petitioner_name || '-';
  }

  get respondentName(): string {
    const res = this.litigants.find((l: any) => l?.is_petitioner === false);
    return res?.name || '-';
  }

  benchLabel(key: string | null | undefined): string {
    if (this.isUnassignedBench(key)) return '-';
    const normalizedKey = String(key ?? '').trim();
    return this.benchConfigurations.find((item) => item.bench_key === normalizedKey)?.label || normalizedKey;
  }

  private isUnassignedBench(key: string | null | undefined): boolean {
    const value = String(key ?? '').trim().toLowerCase();
    return !value || value === 'high court of sikkim' || value === 'high court of skkim';
  }

  get isBenchLocked(): boolean {
    return !this.isUnassignedBench(this.filing?.bench);
  }

  get judgesForSelectedBench(): string[] {
    return this.benchConfigurations.find((item) => item.bench_key === this.selectedBench)?.judge_names || [];
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

