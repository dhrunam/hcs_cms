import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { EfilingService } from '../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-filed-case-details',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './details.html',
  styleUrl: './details.css',
})
export class FiledCaseDetails {
  readonly hiddenHistoryComments = new Set([
    'Document uploaded by advocate.',
    'Document re-uploaded by advocate.',
    'Document sent to scrutiny queue.',
    'Document review item created.',
  ]);

  filingId: number | null = null;
  filing: any = null;
  litigants: any[] = [];
  caseDetails: any = null;
  acts: any[] = [];
  documents: any[] = [];
  selectedDocument: any = null;
  selectedDocumentUrl: SafeResourceUrl | null = null;
  selectedDocumentBlobUrl: string | null = null;
  documentHistory: any[] = [];
  scrutinyChecklist: any[] = [];
  reviewNote = '';
  isLoading = false;
  isSavingReview = false;
  missingFilingId = false;

  constructor(
    private route: ActivatedRoute,
    private efilingService: EfilingService,
    private sanitizer: DomSanitizer,
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      const rawId = params.get('id');
      const nextId = rawId ? Number(rawId) : null;
      this.filingId = nextId && !Number.isNaN(nextId) ? nextId : null;
      this.missingFilingId = !this.filingId;

      if (this.filingId) {
        this.loadWorkspace(this.filingId);
      }
    });
  }

  loadWorkspace(id: number, preferredDocumentId?: number): void {
    this.isLoading = true;

    forkJoin({
      filing: this.efilingService.get_filing_by_id(id),
      litigants: this.efilingService.get_litigant_list_by_filing_id(id),
      caseDetails: this.efilingService.get_case_details_by_filing_id(id),
      acts: this.efilingService.get_acts_by_filing_id(id),
      documents: this.efilingService.get_document_reviews_by_filing_id(id),
    }).subscribe({
      next: ({ filing, litigants, caseDetails, acts, documents }) => {
        this.filing = filing;
        this.litigants = litigants?.results ?? [];
        this.caseDetails = caseDetails?.results?.[0] ?? null;
        this.acts = acts?.results ?? [];
        this.documents = documents?.results ?? [];
        this.loadChecklist();
        this.selectDocument(
          this.documents.find((document) => document.id === preferredDocumentId) ?? this.documents[0] ?? null,
        );
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load scrutiny workspace', error);
        this.isLoading = false;
      },
    });
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
    this.reviewNote = document?.comments ?? '';
    this.updatePreviewUrl(document?.file_url ?? null);

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

  updatePreviewUrl(fileUrl: string | null): void {
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
        this.selectedDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
          this.selectedDocumentBlobUrl,
        );
      },
      error: () => {
        this.selectedDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(fileUrl);
      },
    });
  }

  saveNotes(): void {
    const currentStatus =
      this.selectedDocument?.scrutiny_status === 'REJECTED' ? 'REJECTED' : 'UNDER_SCRUTINY';
    this.submitReview(currentStatus);
  }

  acceptDocument(): void {
    this.submitReview('ACCEPTED');
  }

  rejectDocument(): void {
    this.submitReview('REJECTED');
  }

  submitReview(status: string): void {
    if (!this.selectedDocument?.id || !this.filingId || this.isSavingReview) {
      return;
    }

    this.isSavingReview = true;
    this.efilingService
      .review_document(this.selectedDocument.id, {
        comments: this.reviewNote,
        scrutiny_status: status,
      })
      .subscribe({
        next: () => {
          this.isSavingReview = false;
          this.loadWorkspace(this.filingId!, this.selectedDocument.id);
        },
        error: (error) => {
          console.error('Failed to update review', error);
          this.isSavingReview = false;
        },
      });
  }

  openInNewTab(): void {
    if (this.selectedDocument?.file_url) {
      window.open(this.selectedDocument.file_url, '_blank', 'noopener');
    }
  }

  getStatusLabel(status: string | null): string {
    const normalizedStatus = (status ?? '').trim().toLowerCase();
    if (!normalizedStatus || normalizedStatus === 'submitted' || normalizedStatus === 'under_scrutiny') {
      return 'Under Scrutiny';
    }
    if (normalizedStatus.includes('accept')) {
      return 'Accepted';
    }
    if (normalizedStatus.includes('reject') || normalizedStatus.includes('object')) {
      return 'Rejected';
    }
    if (normalizedStatus === 'draft') {
      return 'Draft';
    }
    return status ?? 'Under Scrutiny';
  }

  getStatusTone(status: string | null): 'warning' | 'success' | 'danger' {
    const label = this.getStatusLabel(status).toLowerCase();
    if (label.includes('accept')) {
      return 'success';
    }
    if (label.includes('reject') || label.includes('object')) {
      return 'danger';
    }
    return 'warning';
  }

  getStatusClass(status: string | null): string {
    const tone = this.getStatusTone(status);
    if (tone === 'success') {
      return 'status-badge-success';
    }
    if (tone === 'danger') {
      return 'status-badge-danger';
    }
    return 'status-badge-warning';
  }

  getDocumentTitle(document: any): string {
    return document?.document_part_name || document?.document_type || 'Uploaded document';
  }

  getDocumentMeta(document: any): string {
    return document?.document_type || 'PDF document';
  }

  getDocumentDate(document: any): string | null {
    return document?.last_reviewed_at ?? document?.last_resubmitted_at ?? document?.updated_at ?? null;
  }

  historyClass(status: string | null): string {
    const tone = this.getStatusTone(status);
    if (tone === 'success') {
      return 'history-success';
    }
    if (tone === 'danger') {
      return 'history-danger';
    }
    return 'history-warning';
  }

  trackById(_: number, item: any): number {
    return item.id;
  }

  get visibleDocumentHistory(): any[] {
    return this.documentHistory.filter((item) => {
      const comment = (item?.comments ?? '').trim();
      return Boolean(comment) && !this.hiddenHistoryComments.has(comment);
    });
  }

  get sortedLitigants(): any[] {
    return [...this.litigants].sort((a, b) => (a?.sequence_number ?? 0) - (b?.sequence_number ?? 0));
  }

  get petitioners(): any[] {
    return this.sortedLitigants.filter((litigant) => litigant.is_petitioner);
  }

  get respondents(): any[] {
    return this.sortedLitigants.filter((litigant) => !litigant.is_petitioner);
  }

  get acceptedCount(): number {
    return this.documents.filter((document) => this.getStatusTone(document.scrutiny_status) === 'success').length;
  }

  get rejectedCount(): number {
    return this.documents.filter((document) => this.getStatusTone(document.scrutiny_status) === 'danger').length;
  }

  get pendingCount(): number {
    return this.documents.filter((document) => this.getStatusTone(document.scrutiny_status) === 'warning').length;
  }
}
