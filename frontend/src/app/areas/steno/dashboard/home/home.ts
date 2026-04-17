import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';

import { ReaderService, StenoQueueItem } from '../../../../services/reader/reader.service';
import { app_url } from '../../../../environment';

@Component({
  selector: 'app-steno-home',
  imports: [CommonModule, FormsModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class StenoHomePage {
  isLoading = false;
  items: StenoQueueItem[] = [];
  selectedFiles: Record<number, File | null> = {};
  signedFiles: Record<number, File | null> = {};
  signatureCopyFiles: Record<number, File | null> = {};
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
          (item) => item.workflow_status !== 'SIGNED_AND_PUBLISHED',
        );
        if (dateItems.length > 0) {
          this.items = dateItems;
          this.isLoading = false;
          return;
        }
        this.readerService.getStenoQueue().subscribe({
          next: (fallbackResp) => {
            this.items = (fallbackResp?.items ?? []).filter(
              (item) => item.workflow_status !== 'SIGNED_AND_PUBLISHED',
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

  onSignatureCopyFileSelected(workflowId: number, event: Event): void {
    const input = event.target as HTMLInputElement;
    const f = input.files?.[0] ?? null;
    this.signatureCopyFiles[workflowId] = f;
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

  shareApprovedDraft(item: any): void {
    this.readerService.shareApprovedDraft({ workflow_id: item.workflow_id }).subscribe({
      next: () => {
        Swal.fire({
          title: 'Shared',
          text: 'Approved draft shared. Other steno can now review, optionally forward to judge, and sign.',
          icon: 'success',
          timer: 1400,
          showConfirmButton: false,
        });
        this.load();
      },
      error: (err) => {
        const msg = err?.error?.detail || 'Failed to share approved draft.';
        Swal.fire('Error', typeof msg === 'string' ? msg : 'Failed to share approved draft.', 'error');
      },
    });
  }

  forwardToJudgeOptional(item: any): void {
    this.readerService.forwardToJudgeOptional({ workflow_id: item.workflow_id }).subscribe({
      next: () => {
        Swal.fire({
          title: 'Forwarded',
          text: 'Draft forwarded to your judge for reference. You can still sign when ready.',
          icon: 'success',
          timer: 1300,
          showConfirmButton: false,
        });
        this.load();
      },
      error: (err) => {
        const msg = err?.error?.detail || 'Failed to forward draft to judge.';
        Swal.fire('Error', typeof msg === 'string' ? msg : 'Failed to forward draft to judge.', 'error');
      },
    });
  }

  uploadSignatureCopy(item: any): void {
    const file = this.signatureCopyFiles[item.workflow_id] ?? null;
    if (!file) {
      Swal.fire('No file', 'Choose signed copy PDF first.', 'warning');
      return;
    }
    if (file.type && file.type !== 'application/pdf') {
      Swal.fire('Invalid type', 'Please choose a PDF file.', 'warning');
      return;
    }
    this.readerService.uploadSignatureCopy(item.workflow_id, file).subscribe({
      next: () => {
        Swal.fire({
          title: 'Uploaded',
          text: 'Signed copy shared with primary steno.',
          icon: 'success',
          timer: 1200,
          showConfirmButton: false,
        });
        this.signatureCopyFiles[item.workflow_id] = null;
        this.load();
      },
      error: (err) => {
        const msg = err?.error?.detail || err?.error?.file?.[0] || 'Failed to upload signed copy.';
        Swal.fire('Error', typeof msg === 'string' ? msg : 'Failed to upload signed copy.', 'error');
      },
    });
  }

  markSignatureComplete(item: any): void {
    this.readerService.markSignatureComplete({ workflow_id: item.workflow_id }).subscribe({
      next: () => {
        Swal.fire({ title: 'Updated', text: 'Signature marked complete.', icon: 'success', timer: 1000, showConfirmButton: false });
        this.load();
      },
      error: (err) => {
        const msg = err?.error?.detail || 'Failed to mark signature.';
        Swal.fire('Error', typeof msg === 'string' ? msg : 'Failed to mark signature.', 'error');
      },
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

  roleLabel(item: any): string {
    return item?.is_primary_steno ? 'Primary Steno Flow' : 'Junior Steno Flow';
  }

  isDivisionBenchFlow(item: any): boolean {
    const rows = Array.isArray(item?.signature_rows) ? item.signature_rows : [];
    if (rows.length > 1) {
      return true;
    }
    const st = String(item?.workflow_status || '');
    return st === 'SHARED_FOR_SIGNATURE' || st === 'SIGNATURES_IN_PROGRESS';
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
    if (typeof item?.can_upload_draft === 'boolean') {
      return item.can_upload_draft;
    }
    const status = item?.workflow_status;
    return (
      status === 'PENDING_UPLOAD' ||
      status === 'UPLOADED_BY_STENO' ||
      status === 'SENT_FOR_JUDGE_APPROVAL' ||
      status === 'CHANGES_REQUESTED'
    );
  }

  canSubmitToJudge(item: any): boolean {
    if (typeof item?.can_submit_to_judge === 'boolean') {
      return item.can_submit_to_judge;
    }
    return !!item?.draft_preview_url && this.canUploadDraft(item);
  }

  showJudgeFeedback(item: any): boolean {
    const st = item?.workflow_status;
    const notes = (item?.judge_approval_notes || '').toString().trim();
    const ann = item?.judge_annotations;
    return st === 'CHANGES_REQUESTED' || !!notes || (Array.isArray(ann) && ann.length > 0);
  }

  canPublishSigned(item: any): boolean {
    if (typeof item?.can_upload_signed_publish === 'boolean') {
      return item.can_upload_signed_publish;
    }
    return (
      (item?.workflow_status === 'JUDGE_APPROVED' ||
        item?.workflow_status === 'SHARED_FOR_SIGNATURE' ||
        item?.workflow_status === 'SIGNATURES_IN_PROGRESS') &&
      item?.judge_approval_status === 'APPROVED'
    );
  }

  canShareApprovedDraft(item: any): boolean {
    if (typeof item?.can_share_approved_draft === 'boolean') {
      return item.can_share_approved_draft;
    }
    return (
      item?.is_primary_steno &&
      item?.workflow_status === 'JUDGE_APPROVED' &&
      item?.judge_approval_status === 'APPROVED'
    );
  }

  isReadOnlyBeforeShare(item: any): boolean {
    return !!item?.is_read_only_view;
  }

  hasCurrentStenoForwardedToJudge(item: any): boolean {
    if (item?.is_primary_steno) {
      return false;
    }
    const rows = Array.isArray(item?.signature_rows) ? item.signature_rows : [];
    if (item?.can_mark_signature_complete || item?.can_forward_to_judge_optional) {
      return rows.some((sr: any) => sr?.signature_status !== 'SIGNED' && !!sr?.forwarded_to_judge);
    }
    return false;
  }

  canForwardToJudgeOptional(item: any): boolean {
    return !!item?.can_forward_to_judge_optional;
  }

  canUploadSignatureCopy(item: any): boolean {
    return !!item?.can_upload_signature_copy;
  }

  isSingleBenchFlow(item: any): boolean {
    return !this.isDivisionBenchFlow(item);
  }

  juniorSignedCopyRows(item: any): any[] {
    const rows = Array.isArray(item?.signature_rows) ? item.signature_rows : [];
    return rows.filter((sr: any) => !!sr?.signed_upload_url);
  }

  collaborationStatus(item: any): string | null {
    const status = String(item?.workflow_status || '');
    const isPrimary = !!item?.is_primary_steno;
    const canSignNow = !!item?.can_mark_signature_complete;
    const hasForwardedOptional = this.hasCurrentStenoForwardedToJudge(item);
    if (canSignNow && !isPrimary) {
      if (hasForwardedOptional) {
        return 'Forwarded To Judge; Upload Signed Copy And Sign';
      }
      if (this.canUploadSignatureCopy(item)) {
        return 'Shared Draft Received; Upload Signed Copy For Primary';
      }
      return 'Shared Draft Received; Sign Pending';
    }
    if (canSignNow && isPrimary) {
      return 'Primary Signature Pending';
    }
    if (isPrimary) {
      if (status === 'JUDGE_APPROVED' && item?.judge_approval_status === 'APPROVED') {
        return 'Ready To Share With Junior Steno';
      }
      if (
        (status === 'SHARED_FOR_SIGNATURE' || status === 'SIGNATURES_IN_PROGRESS') &&
        !item?.all_required_signatures_done
      ) {
        return 'Shared For Signature; Waiting For Remaining Signatures';
      }
      if (item?.all_required_signatures_done && !item?.all_junior_signature_copies_uploaded) {
        return 'Waiting For Junior Signed Copy Upload';
      }
      if (item?.all_required_signatures_done) {
        return 'All Signatures Complete; Ready To Upload & Publish';
      }
      return null;
    }
    if (item?.is_read_only_view) {
      if (
        status === 'JUDGE_APPROVED' ||
        status === 'SHARED_FOR_SIGNATURE' ||
        status === 'SIGNATURES_IN_PROGRESS'
      ) {
        return 'Awaiting Primary Share For Signature';
      }
      return 'Awaiting Primary Draft/Approval';
    }
    return null;
  }

  actionHint(item: any): string | null {
    if (this.isSingleBenchFlow(item)) {
      return 'Single bench: upload draft, send to your judge, then upload final signed order.';
    }
    if (item?.is_primary_steno) {
      if (this.canShareApprovedDraft(item)) {
        return 'Step 1: Share approved draft with junior steno for the same order file.';
      }
      if (!item?.all_required_signatures_done) {
        return 'Waiting for all assigned stenographers to complete signatures.';
      }
      if (!item?.all_junior_signature_copies_uploaded) {
        return 'Waiting for junior signed copy upload back to primary.';
      }
      return 'Step 2: Upload the final fully-signed shared PDF to publish.';
    }
    if (this.canUploadSignatureCopy(item)) {
      return 'Step 1: Upload your signed copy for primary steno.';
    }
    if (item?.can_mark_signature_complete) {
      return 'Step 2: Mark signature complete after signing.';
    }
    if (item?.is_read_only_view) {
      return 'Waiting for primary steno to share approved draft.';
    }
    return null;
  }

  showJuniorMarkSignature(item: any): boolean {
    return !!item?.can_mark_signature_complete && !this.canUploadSignatureCopy(item);
  }

  isPrimaryDivisionBench(item: any): boolean {
    return this.isDivisionBenchFlow(item) && !!item?.is_primary_steno;
  }

  canPrimarySendToJunior(item: any): boolean {
    return this.isPrimaryDivisionBench(item) && this.canShareApprovedDraft(item);
  }

  canJuniorDownloadFromPrimary(item: any): boolean {
    return this.isDivisionBenchFlow(item) && !item?.is_primary_steno && !!item?.draft_preview_url;
  }

  canJuniorSendToJudge(item: any): boolean {
    return this.isDivisionBenchFlow(item) && !item?.is_primary_steno && !!item?.draft_preview_url;
  }

  canJuniorUploadBackToPrimary(item: any): boolean {
    return this.isDivisionBenchFlow(item) && !item?.is_primary_steno && this.canUploadSignatureCopy(item);
  }

  canPrimaryDownloadJuniorPdf(item: any): boolean {
    return this.isPrimaryDivisionBench(item) && this.juniorSignedCopyRows(item).length > 0;
  }
}
