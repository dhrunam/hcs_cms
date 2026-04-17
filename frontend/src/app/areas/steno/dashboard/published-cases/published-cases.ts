import { Component } from "@angular/core";
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';
import { ReaderService, StenoQueueItem } from '../../../../services/reader/reader.service';
import { app_url } from '../../../../environment';

@Component({
  selector: "app-published-cases",
  imports: [CommonModule, FormsModule],
  templateUrl: "./published-cases.html",
  styleUrl: "./published-cases.css",
})
export class PublishedCases {
  isLoading = false;
  items: StenoQueueItem[] = [];
  selectedFiles: Record<number, File | null> = {};
  signedFiles: Record<number, File | null> = {};
  selectedDate = new Date().toISOString().slice(0, 10);
  usedDateFallback = false;

  constructor(private readerService: ReaderService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading = true;
    this.usedDateFallback = false;
    this.readerService.getStenoQueue(this.selectedDate).subscribe({
      next: (resp) => {
        const dateItems = (resp?.items ?? []).filter(
          (item) => item.workflow_status === 'SIGNED_AND_PUBLISHED',
        );
        if (dateItems.length > 0) {
          this.items = dateItems;
          this.isLoading = false;
          return;
        }
        this.readerService.getStenoQueue().subscribe({
          next: (fallbackResp) => {
            this.items = (fallbackResp?.items ?? []).filter(
              (item) => item.workflow_status === 'SIGNED_AND_PUBLISHED',
            );
            this.usedDateFallback = this.items.length > 0;
            this.isLoading = false;
          },
          error: () => {
            this.items = [];
            this.isLoading = false;
          },
        });
      },
      error: () => {
        this.items = [];
        this.isLoading = false;
      },
    });
  }

  onDraftFileSelected(workflowId: number, event: Event): void {
    const input = event.target as HTMLInputElement;
    const f = input.files?.[0] ?? null;
    this.selectedFiles[workflowId] = f;
  }

  onSignedFileSelected(workflowId: number, event: Event): void {
    const input = event.target as HTMLInputElement;
    const f = input.files?.[0] ?? null;
    this.signedFiles[workflowId] = f;
  }

  uploadDraftFile(item: any): void {
    const file = this.selectedFiles[item.workflow_id] ?? null;
    if (!file) {
      Swal.fire('No file', 'Choose a PDF first.', 'warning');
      return;
    }
    if (file.type && file.type !== 'application/pdf') {
      Swal.fire('Invalid type', 'Please choose a PDF file.', 'warning');
      return;
    }
    this.readerService.uploadStenoDraftFile(item.workflow_id, file).subscribe({
      next: () => {
        Swal.fire({ title: 'Draft uploaded', icon: 'success', timer: 900, showConfirmButton: false });
        this.selectedFiles[item.workflow_id] = null;
        this.load();
      },
      error: (err) => {
        const msg = err?.error?.detail || err?.error?.file?.[0] || 'Upload failed.';
        Swal.fire('Error', typeof msg === 'string' ? msg : 'Failed to upload draft.', 'error');
      },
    });
  }


  onDateChange(): void {
    this.load();
  }

  submitToJudge(item: any): void {
    this.readerService.submitStenoToJudge({ workflow_id: item.workflow_id }).subscribe({
      next: () => {
        Swal.fire({ title: 'Sent', text: 'Sent to judge for approval.', icon: 'success', timer: 1000, showConfirmButton: false });
        this.load();
      },
      error: () => Swal.fire('Error', 'Failed to send to judge.', 'error'),
    });
  }

  uploadSignedAndPublish(item: any): void {
    const file = this.signedFiles[item.workflow_id] ?? null;
    if (!file) {
      Swal.fire('No file', 'Choose signed PDF first.', 'warning');
      return;
    }
    if (file.type && file.type !== 'application/pdf') {
      Swal.fire('Invalid type', 'Please choose a PDF file.', 'warning');
      return;
    }
    this.readerService
      .uploadSignedAndPublish(item.workflow_id, file)
      .subscribe({
      next: () => {
        Swal.fire({
          title: 'Published',
          text: 'Signed draft uploaded and published.',
          icon: 'success',
          timer: 1200,
          showConfirmButton: false,
        });
        this.signedFiles[item.workflow_id] = null;
        this.load();
      },
      error: (err) => {
        const msg = err?.error?.detail || err?.error?.file?.[0] || 'Failed to publish signed draft.';
        Swal.fire('Error', typeof msg === 'string' ? msg : 'Failed to publish signed draft.', 'error');
      },
    });
  }

  openDraftUrl(url: string | null | undefined): void {
    if (!url) return;
    const abs = url.startsWith('http') ? url : `${app_url}${url.startsWith('/') ? '' : '/'}${url}`;
    window.open(abs, '_blank', 'noopener,noreferrer');
  }

  statusLabel(status: string | null | undefined): string {
    return String(status || 'PENDING_UPLOAD').replaceAll('_', ' ');
  }

  statusBadgeClass(status: string | null | undefined): string {
    const value = String(status || '');
    if (value === 'PENDING_UPLOAD') return 'badge bg-secondary-subtle text-secondary-emphasis';
    if (value === 'UPLOADED_BY_STENO') return 'badge bg-info-subtle text-info-emphasis';
    if (value === 'SENT_FOR_JUDGE_APPROVAL') return 'badge bg-primary-subtle text-primary-emphasis';
    if (value === 'CHANGES_REQUESTED') return 'badge bg-warning-subtle text-warning-emphasis';
    if (value === 'JUDGE_APPROVED') return 'badge bg-success-subtle text-success-emphasis';
    if (value === 'SIGNED_AND_PUBLISHED') return 'badge bg-dark-subtle text-dark-emphasis';
    return 'badge bg-light text-dark';
  }

  canUploadDraft(item: any): boolean {
    const status = item?.workflow_status;
    return (
      status === 'PENDING_UPLOAD' ||
      status === 'UPLOADED_BY_STENO' ||
      status === 'SENT_FOR_JUDGE_APPROVAL' ||
      status === 'CHANGES_REQUESTED'
    );
  }

  canSubmitToJudge(item: any): boolean {
    return !!item?.draft_preview_url && this.canUploadDraft(item);
  }

  showJudgeFeedback(item: any): boolean {
    const st = item?.workflow_status;
    const notes = (item?.judge_approval_notes || '').toString().trim();
    const ann = item?.judge_annotations;
    return st === 'CHANGES_REQUESTED' || !!notes || (Array.isArray(ann) && ann.length > 0);
  }

  canPublishSigned(item: any): boolean {
    return (
      (item?.workflow_status === 'JUDGE_APPROVED' ||
        item?.workflow_status === 'SHARED_FOR_SIGNATURE' ||
        item?.workflow_status === 'SIGNATURES_IN_PROGRESS') &&
      item?.judge_approval_status === 'APPROVED'
    );
  }
}

