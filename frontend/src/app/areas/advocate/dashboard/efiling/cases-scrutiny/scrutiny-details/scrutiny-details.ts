import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';
import { forkJoin } from 'rxjs';
import { ToastrService } from 'ngx-toastr';
import Swal from 'sweetalert2';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-scrutiny-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './scrutiny-details.html',
  styleUrl: './scrutiny-details.css',
})
export class ScrutinyDetails {
  readonly hiddenHistoryComments = new Set([
    'Document uploaded by advocate.',
    'Document re-uploaded by advocate.',
    'Document sent to scrutiny queue.',
    'Document review item created.',
  ]);

  filingId: number | null = null;
  filing: any = null;
  documents: any[] = [];
  groupedDocuments: Array<{ document_type: string; items: any[] }> = [];
  litigantList: any[] = [];
  caseDetails: any = null;
  actList: any[] = [];
  selectedDocument: any = null;
  selectedDocumentUrl: SafeResourceUrl | null = null;
  selectedDocumentBlobUrl: string | null = null;
  documentHistory: any[] = [];
  isLoading = false;
  isReplacing = false;
  notesPopupOpen = false;
  canShowReplaceBtn: boolean = false;
  pendingReplacements: Array<{ documentId: number; document: any; file: File }> = [];
  activeTab: 'filing' | 'documents' | 'ia' = 'filing';
  iaList: any[] = [];
  iaDocuments: any[] = [];
  groupedIaDocuments: Array<{ document_type: string; items: any[] }> = [];
  selectedIaDocument: any = null;
  selectedIaDocumentUrl: SafeResourceUrl | null = null;
  selectedIaDocumentBlobUrl: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private efilingService: EfilingService,
    private sanitizer: DomSanitizer,
    private toastr: ToastrService,
  ) {}

  openNotesPopup(): void {
    this.notesPopupOpen = true;
  }

  closeNotesPopup(): void {
    this.notesPopupOpen = false;
  }

  setActiveTab(tab: 'filing' | 'documents' | 'ia'): void {
    this.activeTab = tab;
  }

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      const rawId = params.get('id');
      const nextId = rawId ? Number(rawId) : null;
      this.filingId = nextId && !Number.isNaN(nextId) ? nextId : null;
      if (this.filingId) {
        this.loadDetails(this.filingId);
      }
    });
  }

  loadDetails(id: number, preferredDocumentId?: number): void {
    this.isLoading = true;
    forkJoin({
      filing: this.efilingService.get_filing_by_id(id),
      documents: this.efilingService.get_document_reviews_by_filing_id(id, false),
      iaDocuments: this.efilingService.get_document_reviews_by_filing_id(id, true),
      litigants: this.efilingService.get_litigant_list_by_filing_id(id),
      caseDetails: this.efilingService.get_case_details_by_filing_id(id),
      acts: this.efilingService.get_acts_by_filing_id(id),
      ias: this.efilingService.get_ias_by_efiling_id(id),
    }).subscribe({
      next: ({ filing, documents, iaDocuments, litigants, caseDetails, acts, ias }) => {
        this.filing = filing;
        this.documents = documents?.results ?? [];
        this.groupedDocuments = this.groupDocumentsByType(this.documents);
        this.iaDocuments = iaDocuments?.results ?? [];
        this.groupedIaDocuments = this.groupDocumentsByType(this.iaDocuments);
        this.litigantList = litigants?.results ?? [];
        this.caseDetails = caseDetails?.results?.[0] ?? null;
        this.actList = acts?.results ?? [];
        console.log('Act llist is', this.actList);
        this.iaList = Array.isArray(ias) ? ias : (ias?.results ?? []);
        this.selectIaDocument(this.groupedIaDocuments[0]?.items[0] ?? null);
        this.selectDocument(
          this.documents.find((document) => document.id === preferredDocumentId) ??
            this.documents[0] ??
            null,
        );
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load scrutiny details', error);
        this.isLoading = false;
      },
    });
  }

  groupDocumentsByType(docs: any[]): Array<{ document_type: string; items: any[] }> {
    if (!Array.isArray(docs) || docs.length === 0) return [];

    // Preserve original ordering (as returned by the API) while grouping by "main document type".
    const map = new Map<string, any[]>();
    for (const doc of docs) {
      const type = (doc?.document_type ?? '').trim() || 'Main Document';
      const bucket = map.get(type);
      if (bucket && !bucket.some((item: any) => item.file_part_path === null)) {
        bucket.push(doc);
      } else {
        map.set(type, [doc]);
      }
    }

    return Array.from(map.entries()).map(([document_type, items]) => ({ document_type, items }));
  }

  selectDocument(document: any): void {
    this.selectedDocument = document;
    // this.canShowReplaceBtn = this.canShowReplaceButton(document);
    this.canShowReplaceBtn =
      document && document.scrutiny_status.toLowerCase().includes('rejected');
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

  triggerReplace(input: HTMLInputElement, document: any): void {
    input.value = '';
    input.click();
  }

  startReplace(document: any, input: HTMLInputElement, event?: Event): void {
    event?.stopPropagation();
    this.selectDocument(document);
    (input as any)._replaceDoc = document;
    this.triggerReplace(input, document);
  }

  startReplaceIa(doc: any, input: HTMLInputElement, event?: Event): void {
    event?.stopPropagation();
    this.selectIaDocument(doc);
    (input as any)._replaceDoc = doc;
    input.value = '';
    input.click();
  }

  addPendingReplacement(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    const doc = (input as any)._replaceDoc ?? this.selectedDocument;

    if (!file || !doc?.id) {
      input.value = '';
      return;
    }

    const existing = this.pendingReplacements.find((p) => p.documentId === doc.id);
    if (existing) {
      existing.file = file;
    } else {
      this.pendingReplacements.push({ documentId: doc.id, document: doc, file });
    }
    input.value = '';
  }

  removePendingReplacement(documentId: number): void {
    this.pendingReplacements = this.pendingReplacements.filter((p) => p.documentId !== documentId);
  }

  hasPendingReplacement(documentId: number): boolean {
    return this.pendingReplacements.some((p) => p.documentId === documentId);
  }

  getPendingFileForDocument(documentId: number): File | null {
    const p = this.pendingReplacements.find((pr) => pr.documentId === documentId);
    return p?.file ?? null;
  }

  viewPendingFile(documentId: number): void {
    const p = this.pendingReplacements.find((pr) => pr.documentId === documentId);
    if (!p?.file) return;
    const url = URL.createObjectURL(p.file);
    window.open(url, '_blank', 'noopener');
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }

  async submitAllReplacements(): Promise<void> {
    if (this.pendingReplacements.length === 0 || this.isReplacing) return;

    const count = this.pendingReplacements.length;
    const confirmed = await Swal.fire({
      title: 'Replace All Documents?',
      text: `You are about to replace ${count} document${count > 1 ? 's' : ''} with new files. This action cannot be undone.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Yes, replace all',
      cancelButtonText: 'Cancel',
    });

    if (!confirmed.isConfirmed) return;

    const proceed = await this.promptOtpAndProceed();
    if (!proceed) return;

    this.isReplacing = true;
    const toReplace = [...this.pendingReplacements];
    this.pendingReplacements = [];

    const replaceNext = (index: number): void => {
      if (index >= toReplace.length) {
        this.isReplacing = false;
        this.loadDetails(this.filingId!);
        Swal.fire({
          title: 'Replaced',
          text: `${toReplace.length} document(s) have been replaced successfully.`,
          icon: 'success',
          timer: 2000,
          showConfirmButton: false,
        });
        return;
      }

      const { documentId, file } = toReplace[index];
      this.efilingService.replace_document_review_item(documentId, file).subscribe({
        next: () => replaceNext(index + 1),
        error: (error) => {
          console.error('Failed to replace document', error);
          this.isReplacing = false;
          this.pendingReplacements = [...toReplace.slice(index)];
          Swal.fire({
            title: 'Error',
            text: 'Failed to replace document. Please try again.',
            icon: 'error',
          });
        },
      });
    };

    replaceNext(0);
  }

  private async promptOtpAndProceed(): Promise<boolean> {
    this.toastr.success('OTP has been sent successfully.', '', {
      timeOut: 3000,
      closeButton: true,
    });

    let resolved = false;
    return new Promise<boolean>((resolve) => {
      const finish = (value: boolean) => {
        if (resolved) return;
        resolved = true;
        resolve(value);
      };

      Swal.fire({
        title: 'Enter OTP',
        html:
          '<div style="display:flex;gap:8px;justify-content:center">' +
          ['otp-1', 'otp-2', 'otp-3', 'otp-4']
            .map(
              (id) =>
                `<input id="${id}" type="text" inputmode="numeric" maxlength="1" style="width:48px;height:48px;text-align:center;font-size:20px;border:1px solid #d1d5db;border-radius:8px;" />`,
            )
            .join('') +
          '<div id="otp-status" style="margin-top:12px;font-size:14px;text-align:center"></div>',
        showCancelButton: true,
        showConfirmButton: false,
        allowOutsideClick: false,
        didOpen: () => {
          const ids = ['otp-1', 'otp-2', 'otp-3', 'otp-4'];
          const inputs = ids
            .map((id) => document.getElementById(id) as HTMLInputElement | null)
            .filter((el): el is HTMLInputElement => !!el);
          const statusEl = document.getElementById('otp-status');

          const setStatus = (message: string, color: string) => {
            if (!statusEl) return;
            statusEl.textContent = message;
            statusEl.style.color = color;
          };

          const getOtp = () => inputs.map((el) => el.value || '').join('');

          const validateOtp = () => {
            const otp = getOtp();
            if (otp.length < 4) {
              setStatus('', '');
              return;
            }
            if (otp !== '0000') {
              setStatus('OTP error. Please try again.', '#dc2626');
              return;
            }
            setStatus('OTP verified.', '#16a34a');
            Swal.close();
            finish(true);
          };

          inputs.forEach((input, index) => {
            input.addEventListener('input', () => {
              input.value = input.value.replace(/\D/g, '').slice(0, 1);
              if (input.value && inputs[index + 1]) inputs[index + 1].focus();
              validateOtp();
            });
            input.addEventListener('keydown', (event) => {
              if (event.key === 'Backspace' && !input.value && inputs[index - 1]) {
                inputs[index - 1].focus();
              }
            });
          });
          inputs[0]?.focus();
        },
      }).then((result) => {
        if (result.dismiss === Swal.DismissReason.cancel) finish(false);
      });
    });
  }

  openInNewTab(): void {
    if (this.selectedDocument?.file_url) {
      window.open(this.selectedDocument.file_url, '_blank', 'noopener');
    }
  }

  getStatusLabel(status: string | null): string {
    const normalizedStatus = (status ?? '').trim().toLowerCase();
    if (
      !normalizedStatus ||
      normalizedStatus === 'submitted' ||
      normalizedStatus === 'under_scrutiny'
    ) {
      return 'Under Scrutiny';
    }
    if (normalizedStatus.includes('accept')) {
      return 'Accepted';
    }
    if (normalizedStatus.includes('reject') || normalizedStatus.includes('object')) {
      return 'Rejected';
    }
    return status ?? 'Under Scrutiny';
  }

  getStatusClass(status: string | null): string {
    const label = this.getStatusLabel(status).toLowerCase();
    if (label.includes('accept')) {
      return 'status-badge-success';
    }
    if (label.includes('reject')) {
      return 'status-badge-danger';
    }
    return 'status-badge-warning';
  }

  historyClass(status: string | null): string {
    if (this.getStatusClass(status) === 'status-badge-success') {
      return 'history-success';
    }
    if (this.getStatusClass(status) === 'status-badge-danger') {
      return 'history-danger';
    }
    return 'history-warning';
  }

  canReplace(document: any): boolean {
    return Boolean(document?.can_replace && document?.document);
  }

  canReplaceIa(doc: any): boolean {
    return this.canReplace(doc);
  }

  trackById(_: number, item: any): number {
    return item.id;
  }

  trackByGroupIndex(index: number, group: any): string {
    return `${index}__${group?.document_type ?? 'unknown'}`;
  }

  private extractFileName(value: string | null | undefined): string {
    const raw = (value ?? '').trim();
    if (!raw) return '';

    // Remove query string if it's a URL.
    const withoutQuery = raw.split('?')[0];
    const parts = withoutQuery.split('/');
    return parts[parts.length - 1] || '';
  }

  getDocumentFileLabel(document: any): string {
    const partName = (document?.document_part_name ?? '').trim();
    if (partName) return partName;

    const fileUrl = document?.file_url ?? document?.file_part_path;
    const fileName = this.extractFileName(fileUrl);
    return fileName || 'Document';
  }

  get visibleDocumentHistory(): any[] {
    return this.documentHistory.filter((item) => {
      const comment = (item?.comments ?? '').trim();
      return Boolean(comment) && !this.hiddenHistoryComments.has(comment);
    });
  }

  get sortedLitigants(): any[] {
    return [...this.litigantList].sort(
      (a, b) => (a?.sequence_number ?? 0) - (b?.sequence_number ?? 0),
    );
  }

  get petitioners(): any[] {
    return this.sortedLitigants.filter((litigant) => litigant.is_petitioner);
  }

  get respondents(): any[] {
    return this.sortedLitigants.filter((litigant) => !litigant.is_petitioner);
  }

  getActName(act: any): string {
    return act?.act?.actname ?? act?.actname ?? '-';
  }

  selectIaDocument(document: any): void {
    this.selectedIaDocument = document;
    if (this.selectedIaDocumentBlobUrl) {
      URL.revokeObjectURL(this.selectedIaDocumentBlobUrl);
      this.selectedIaDocumentBlobUrl = null;
    }
    if (!document?.file_url) {
      this.selectedIaDocumentUrl = null;
      return;
    }
    this.selectedIaDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(document.file_url);
    this.efilingService.fetch_document_blob(document.file_url).subscribe({
      next: (blob) => {
        this.selectedIaDocumentBlobUrl = URL.createObjectURL(blob);
        this.selectedIaDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
          this.selectedIaDocumentBlobUrl,
        );
      },
      error: () => {
        this.selectedIaDocumentUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
          document.file_url,
        );
      },
    });
  }
}
