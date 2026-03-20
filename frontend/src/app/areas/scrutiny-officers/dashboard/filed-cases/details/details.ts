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
  groupedDocuments: Array<{ document_type: string; items: any[] }> = [];
  selectedDocument: any = null;
  selectedDocumentUrl: SafeResourceUrl | null = null;
  selectedDocumentBlobUrl: string | null = null;
  documentHistory: any[] = [];
  scrutinyChecklist: any[] = [];
  reviewNote = '';
  isLoading = false;
  isSavingReview = false;
  isSubmittingApprovedCase = false;
  missingFilingId = false;
  activeTab: 'filing' | 'documents' = 'filing';

  constructor(
    private route: ActivatedRoute,
    private efilingService: EfilingService,
    private sanitizer: DomSanitizer,
  ) {}

  setActiveTab(tab: 'filing' | 'documents'): void {
    this.activeTab = tab;
  }

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
        this.groupedDocuments = this.groupDocumentsByType(this.documents);
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

  groupDocumentsByType(docs: any[]): Array<{ document_type: string; items: any[] }> {
    if (!Array.isArray(docs) || docs.length === 0) return [];

    const map = new Map<string, any[]>();
    for (const doc of docs) {
      const type = (doc?.document_type ?? '').trim() || 'Main Document';
      const bucket = map.get(type);
      if (bucket) {
        bucket.push(doc);
      } else {
        map.set(type, [doc]);
      }
    }

    return Array.from(map.entries()).map(([document_type, items]) => ({ document_type, items }));
  }

  acceptDocument(): void {
    this.submitReview('ACCEPTED');
  }

  rejectDocument(): void {
    // Rejecting a document also persists the current notes in the same review update.
    this.submitReview('REJECTED');
  }

  submitApprovedFiling(): void {
    if (!this.canSubmitApprovedFiling || !this.filingId) {
      return;
    }

    this.isSubmittingApprovedCase = true;
    this.efilingService.submit_approved_filing(this.filingId).subscribe({
      next: (filing) => {
        this.isSubmittingApprovedCase = false;
        this.filing = filing;
      },
      error: (error) => {
        console.error('Failed to submit approved filing', error);
        this.isSubmittingApprovedCase = false;
      },
    });
  }

  submitReview(status: string): void {
    if (!this.selectedDocument?.id || !this.filingId || this.isSavingReview) {
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
          this.refreshFilingSummary();
          this.selectDocument(this.getNextDocumentForReview(currentDocumentId));
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

  private extractFileName(value: string | null | undefined): string {
    const raw = (value ?? '').trim();
    if (!raw) return '';

    const withoutQuery = raw.split('?')[0];
    const parts = withoutQuery.split('/');
    return parts[parts.length - 1] || '';
  }

  getDocumentTitle(document: any): string {
    const partName = (document?.document_part_name ?? '').trim();
    if (partName) return partName;

    const fileUrl = document?.file_url ?? document?.file_part_path;
    const fileName = this.extractFileName(fileUrl);
    return fileName || 'Uploaded document';
  }

  getDocumentMeta(document: any): string {
    return 'PDF document';
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

  trackByGroupIndex(index: number, group: any): string {
    return `${index}__${group?.document_type ?? 'unknown'}`;
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
  getActName(act: any): string {
    return act?.act?.actname ?? act?.actname ?? '-';
  }
  private applyReviewedDocument(updatedDocument: any): void {
    if (!updatedDocument?.id) {
      return;
    }

    this.documents = this.documents.map((document) =>
      document.id === updatedDocument.id ? { ...document, ...updatedDocument } : document,
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
        console.error('Failed to refresh filing summary', error);
      },
    });
  }

  private getNextDocumentForReview(currentDocumentId: number): any {
    const nextPendingDocument =
      this.documents.find(
        (document) =>
          document.id !== currentDocumentId && this.getStatusTone(document.scrutiny_status) === 'warning',
      ) ?? null;

    if (nextPendingDocument) {
      return nextPendingDocument;
    }

    const currentIndex = this.documents.findIndex((document) => document.id === currentDocumentId);
    if (currentIndex === -1) {
      return this.documents[0] ?? null;
    }

    return this.documents[currentIndex + 1] ?? this.documents[currentIndex - 1] ?? this.documents[currentIndex];
  }

  get allDocumentsApproved(): boolean {
    return (
      this.documents.length > 0 &&
      this.documents.every((document) => this.getStatusTone(document?.scrutiny_status) === 'success')
    );
  }

  get canSubmitApprovedFiling(): boolean {
    return Boolean(
      this.filingId &&
        !this.isSubmittingApprovedCase &&
        !this.filing?.case_number &&
        this.allDocumentsApproved,
    );
  }
}
