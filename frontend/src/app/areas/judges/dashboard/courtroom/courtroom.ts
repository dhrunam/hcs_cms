import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ActivatedRoute, RouterLink } from '@angular/router';
import Swal from 'sweetalert2';

import { CourtroomService } from '../../../../services/judge/courtroom.service';

@Component({
  selector: 'app-judge-courtroom',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './courtroom.html',
  styleUrl: './courtroom.css',
})
export class JudgeCourtroomPage {
  efilingId: number | null = null;
  forwardedForDate: string | null = null;

  isLoading = false;
  loadError = '';

  caseSummary: any = null;
  decisionStatus: 'APPROVED' | 'DECLINED' = 'DECLINED';
  decisionNotes = '';
  allCaseDocuments: any[] = [];
  docSearch = '';
  previewDocument: any = null;
  previewDocumentUrl: SafeResourceUrl | null = null;
  previewDocumentBlobUrl: string | null = null;
  previewLoadError = '';

  canWrite = false;

  constructor(
    private route: ActivatedRoute,
    private courtroomService: CourtroomService,
    private sanitizer: DomSanitizer,
  ) {}

  ngOnInit(): void {
    this.canWrite = this.readCanWrite();

    const idRaw = this.route.snapshot.paramMap.get('id');
    this.efilingId = idRaw ? Number(idRaw) : null;

    this.forwardedForDate = this.route.snapshot.queryParamMap.get('forwarded_for_date');
    if (!this.efilingId || !this.forwardedForDate) {
      this.loadError = 'Missing case id or forwarded_for_date.';
      return;
    }

    this.loadCaseSummary();
  }

  private readCanWrite(): boolean {
    try {
      const raw = sessionStorage.getItem('user_groups');
      const groups = raw ? JSON.parse(raw) : [];
      return Array.isArray(groups) && groups.some((g) => ['JUDGE_CJ', 'JUDGE_J1', 'JUDGE_J2'].includes(String(g)));
    } catch {
      return false;
    }
  }

  private loadCaseSummary(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.isLoading = true;
    this.loadError = '';

    this.courtroomService.getCaseSummary(this.efilingId, this.forwardedForDate).subscribe({
      next: (resp) => {
        this.caseSummary = resp ?? null;
        this.forwardedForDate = resp?.forwarded_for_date ?? this.forwardedForDate;
        const existingStatus = resp?.judge_decision?.status;
        if (existingStatus === 'APPROVED' || existingStatus === 'DECLINED') {
          this.decisionStatus = existingStatus;
        }
        this.decisionNotes = resp?.judge_decision?.decision_notes ?? '';
        this.loadCaseDocuments();
        this.isLoading = false;
      },
      error: (err) => {
        console.warn('Failed to load courtroom case summary', err);
        this.loadError = 'Failed to load case details.';
        this.isLoading = false;
      },
    });
  }

  submitDecision(): void {
    if (!this.canWrite || !this.efilingId || !this.forwardedForDate) return;
    // Note: listingDate is now optional.
    if (this.decisionStatus === 'DECLINED' && !(this.decisionNotes || '').trim()) {
      Swal.fire({ title: 'Remarks Required', text: 'Please provide remarks for decline.', icon: 'warning' });
      return;
    }
    Swal.fire({
      title: 'Save decision?',
      text: 'Are you sure you want to approve/decline this case request?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, save',
    }).then((res) => {
      if (!res.isConfirmed) return;

      this.courtroomService
        .saveDecision({
          efiling_id: this.efilingId!,
          forwarded_for_date: this.forwardedForDate!,
          status: this.decisionStatus,
          decision_notes: this.decisionNotes || null,
        })
        .subscribe({
          next: () => {
            Swal.fire({ title: 'Saved', text: 'Decision saved.', icon: 'success', timer: 1000, showConfirmButton: false });
          },
          error: (err) => {
            console.warn('save decision failed', err);
            Swal.fire({ title: 'Error', text: 'Failed to save decision.', icon: 'error' });
          },
        });
    });
  }

  private loadCaseDocuments(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.courtroomService.getCaseDocuments(this.efilingId, this.forwardedForDate, false).subscribe({
      next: (resp) => {
        this.allCaseDocuments = resp?.items ?? [];
        if (this.allCaseDocuments.length && !this.previewDocument) {
          this.selectPreviewDocument(this.allCaseDocuments[0]);
        }
      },
      error: (err) => {
        console.warn('Failed to load case documents', err);
        this.allCaseDocuments = [];
      },
    });
  }

  get filteredDocuments(): any[] {
    const q = this.docSearch.trim().toLowerCase();
    if (!q) return this.allCaseDocuments;
    return this.allCaseDocuments.filter((d) => {
      const name = String(d?.document_part_name || d?.document_type || '').toLowerCase();
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
      this.previewLoadError = '';
      return;
    }
    const resolvedUrl = fileUrl ? this.courtroomService.resolveDocumentUrl(fileUrl) : '';
    if (fileUrl) {
      this.previewDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(resolvedUrl);
    }
    this.previewLoadError = '';
    const stream$ = docId
      ? this.courtroomService.fetchDocumentBlobByIndex(docId)
      : this.courtroomService.fetchDocumentBlob(resolvedUrl);
    stream$.subscribe({
      next: (blob) => {
        this.previewDocumentBlobUrl = URL.createObjectURL(blob);
        this.previewDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.previewDocumentBlobUrl);
      },
      error: () => {
        this.previewDocumentUrl = null;
        this.previewLoadError = 'Unable to load this PDF preview (file missing or moved).';
      },
    });
  }

  setDecisionStatus(status: 'APPROVED' | 'DECLINED'): void {
    this.decisionStatus = status;
  }
}

