import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';
import { catchError, forkJoin, of } from 'rxjs';
import { ToastrService } from 'ngx-toastr';
import Swal from 'sweetalert2';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
import { PaymentService } from '../../../../../../services/payment/payment.service';
import { getValidationErrorMessage, validatePdfOcr, validatePdfSize } from '../../../../../../utils/pdf-validation';
import {
  EfilingDocumentIndexGroup,
  firstClickableEfilingDocumentIndexInGrouped,
  firstClickableEfilingDocumentIndexInList,
  groupEfilingDocumentIndexesByType,
  isEfilingDocumentIndexClickable,
  trackByEfilingDocumentIndexRowId,
} from '../../../../../../utils/efiling-document-index-tree';

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
  groupedDocuments: EfilingDocumentIndexGroup[] = [];
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
  selectedIaDocument: any = null;
  selectedIaDocumentUrl: SafeResourceUrl | null = null;
  selectedIaDocumentBlobUrl: string | null = null;
  paymentOutcome: 'success' | 'failed' | null = null;
  paymentDetails:
    | {
        txnId?: string;
        paidAt?: string;
        referenceNo?: string;
        amount?: string;
        paymentMode?: 'online' | 'offline';
        bankReceipt?: string;
        paymentDate?: string;
      }
    | null = null;

  constructor(
    private route: ActivatedRoute,
    private efilingService: EfilingService,
    private paymentService: PaymentService,
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
      payment: this.paymentService.latest(id).pipe(catchError(() => of(null))),
    }).subscribe({
      next: ({ filing, documents, iaDocuments, litigants, caseDetails, acts, ias, payment }) => {
        this.filing = filing;
        this.documents = documents?.results ?? [];
        this.groupedDocuments = this.groupDocumentsByType(this.documents);
        this.iaDocuments = iaDocuments?.results ?? [];
        this.litigantList = litigants?.results ?? [];
        this.caseDetails = caseDetails?.results?.[0] ?? null;
        this.actList = acts?.results ?? [];
        console.log('Act llist is', this.actList);
        this.iaList = Array.isArray(ias) ? ias : (ias?.results ?? []);
        this.updatePaymentDetails(payment);
        const firstWithDocs = this.iaWithDocuments.find((i) => i.documents.length > 0);
        this.selectIaDocument(
          firstWithDocs
            ? this.firstClickableInGroupedDocs(firstWithDocs.groupedDocs)
            : null,
        );
        const preferred =
          preferredDocumentId != null
            ? (this.documents.find((d) => d.id === preferredDocumentId) ?? null)
            : null;
        const initialPleading =
          preferred && this.isDocumentIndexClickable(preferred)
            ? preferred
            : this.firstClickableInDocList(this.documents);
        this.selectDocument(initialPleading ?? null);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load scrutiny details', error);
        this.isLoading = false;
      },
    });
  }

  private updatePaymentDetails(tx: any): void {
    if (!tx || (!tx.txn_id && !tx.reference_no && !tx.status)) {
      this.paymentOutcome = null;
      this.paymentDetails = null;
      return;
    }
    const statusRaw = String(tx.status || '').toLowerCase();
    const paymentMode =
      String(tx.payment_mode || '').toLowerCase() === 'offline' ? 'offline' : 'online';
    if (
      /(success|paid|complete|ok)/i.test(statusRaw) ||
      (paymentMode === 'offline' &&
        !!tx.bank_receipt &&
        /(offline_submitted|submitted|pending|success|paid|complete|ok)/i.test(statusRaw))
    ) {
      this.paymentOutcome = 'success';
    } else if (statusRaw) {
      this.paymentOutcome = 'failed';
    } else {
      this.paymentOutcome = null;
    }
    this.paymentDetails = {
      txnId: tx.txn_id || undefined,
      paidAt: tx.payment_datetime || tx.paid_at || undefined,
      referenceNo: tx.reference_no || undefined,
      amount: tx.amount || tx.court_fees || undefined,
      paymentMode,
      bankReceipt: tx.bank_receipt || undefined,
      paymentDate: tx.payment_date || undefined,
    };
  }

  groupDocumentsByType(docs: any[]): EfilingDocumentIndexGroup[] {
    return groupEfilingDocumentIndexesByType(docs);
  }

  isDocumentIndexClickable(doc: any): boolean {
    return isEfilingDocumentIndexClickable(doc);
  }

  advocateDocumentRowClick(doc: any): void {
    if (!this.isDocumentIndexClickable(doc)) return;
    this.selectDocument(doc);
  }

  advocateDocumentRowKeydown(event: Event, doc: any): void {
    if (!this.isDocumentIndexClickable(doc)) return;
    event.preventDefault();
    this.selectDocument(doc);
  }

  advocateIaDocumentRowClick(doc: any): void {
    if (!this.isDocumentIndexClickable(doc)) return;
    this.selectIaDocument(doc);
  }

  advocateIaDocumentRowKeydown(event: Event, doc: any): void {
    if (!this.isDocumentIndexClickable(doc)) return;
    event.preventDefault();
    this.selectIaDocument(doc);
  }

  private firstClickableInDocList(docs: any[]): any | null {
    return firstClickableEfilingDocumentIndexInList(docs);
  }

  private firstClickableInGroupedDocs(grouped: EfilingDocumentIndexGroup[]): any | null {
    return firstClickableEfilingDocumentIndexInGrouped(grouped);
  }

  readonly trackByRowDocumentId = trackByEfilingDocumentIndexRowId;

  selectDocument(document: any): void {
    this.selectedDocument = document;
    this.canShowReplaceBtn = Boolean(
      document?.scrutiny_status?.toLowerCase().includes('rejected'),
    );
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

  async addPendingReplacement(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    const doc = (input as any)._replaceDoc ?? this.selectedDocument;

    if (!file || !doc?.id) {
      input.value = '';
      return;
    }

    if (file.type !== 'application/pdf') {
      this.toastr.error('Please select a PDF file.');
      input.value = '';
      return;
    }

    const sizeCheck = validatePdfSize(file);
    if (!sizeCheck.valid && sizeCheck.error) {
      this.toastr.error(sizeCheck.error);
      input.value = '';
      return;
    }

    const ocrCheck = await validatePdfOcr(file);
    if (!ocrCheck.valid && ocrCheck.error) {
      this.toastr.error(ocrCheck.error);
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
            text: getValidationErrorMessage(error) || 'Failed to replace document. Please try again.',
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
    const s = (status ?? '').trim().toLowerCase();
    if (!s) return 'Under Scrutiny';
    if (s === 'accepted' || s.includes('accept')) return 'Accepted';
    if (s === 'rejected' || s.includes('reject') || s.includes('object') || s.includes('partial')) return 'Rejected';
    if (s === 'draft') return 'Draft';
    if (s === 'under_scrutiny' || s === 'under scrutiny' || s.includes('submitted') || s.includes('scrutiny')) return 'Under Scrutiny';
    return (status ?? 'Under Scrutiny').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  getIaStatusLabel(status: string | null): string {
    const s = (status ?? '').trim().toLowerCase();
    if (!s) return 'Pending';
    if (s === 'accepted' || s.includes('accept')) return 'Accepted';
    if (s === 'rejected' || s.includes('reject') || s.includes('partial')) return 'Rejected';
    if (s === 'draft') return 'Draft';
    if (s === 'under_scrutiny' || s === 'under scrutiny' || s.includes('submitted')) return 'Under Scrutiny';
    return (status ?? 'Pending').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
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

  getIaStatusBadgeClass(status: string | null): string {
    const s = (status ?? '').trim().toLowerCase();
    if (s.includes('accept')) return 'status-badge-success';
    if (s.includes('reject') || s.includes('partial')) return 'status-badge-danger';
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

  get iaWithDocuments(): Array<{
    ia: any;
    documents: any[];
    groupedDocs: EfilingDocumentIndexGroup[];
  }> {
    return this.iaList.map((ia) => {
      const iaNum = (ia?.ia_number ?? '').trim();
      const documents = this.iaDocuments.filter(
        (doc) => ((doc?.ia_number ?? '').trim() || null) === (iaNum || null),
      );
      return {
        ia,
        documents,
        groupedDocs: this.groupDocumentsByType(documents),
      };
    });
  }

  trackByIaItem(_: number, item: { ia: any }): number {
    return item?.ia?.id ?? 0;
  }

  selectedIaDocumentBelongsToIa(item: { documents: any[] }): boolean {
    if (!this.selectedIaDocument?.id || !item?.documents?.length) return false;
    return item.documents.some((d) => d?.id === this.selectedIaDocument?.id);
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

  getDocumentTitle(document: any): string {
    const partName = (document?.document_part_name ?? '').trim();
    if (partName) return partName;

    const fileUrl = document?.file_url ?? document?.file_part_path;
    const fileName = this.extractFileName(fileUrl);
    return fileName || 'Index entry';
  }

  getDocumentDate(document: any): string | null {
    return (
      document?.last_reviewed_at ??
      document?.last_resubmitted_at ??
      document?.updated_at ??
      null
    );
  }

  getDocumentStatusLabel(document: any): string {
    const draftStatus = (document?.draft_scrutiny_status ?? '').trim();
    if (draftStatus) {
      const baseLabel = this.getStatusLabel(draftStatus);
      return baseLabel === 'Under Scrutiny' ? baseLabel : `Draft ${baseLabel}`;
    }
    return this.getStatusLabel(document?.scrutiny_status ?? null);
  }

  getDocumentStatusClass(document: any): string {
    const draftStatus = (document?.draft_scrutiny_status ?? '').trim();
    return this.getStatusClass(draftStatus || document?.scrutiny_status || null);
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
