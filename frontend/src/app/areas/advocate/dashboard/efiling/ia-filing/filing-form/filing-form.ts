import { CommonModule } from '@angular/common';
import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Params, Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { forkJoin } from 'rxjs';
import { ToastrService } from 'ngx-toastr';
import Swal from 'sweetalert2';
import { app_url } from '../../../../../../environment';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
import { PaymentService } from '../../../../../../services/payment/payment.service';
import {
  getValidationErrorMessage,
  validatePdfFiles,
  validatePdfOcrForFiles,
} from '../../../../../../utils/pdf-validation';
import {
  formatPartyLine,
  formatPetitionerVsRespondent,
  getOrderedPartyNames,
} from '../../../../../../utils/petitioner-vs-respondent';
import {
  EXISTING_CASE_LITIGANT_OPTIONS,
  ExistingCaseLitigantType,
} from '../../document-filing/create/create';
import { UploadDocuments } from '../../new-filing/upload-documents/upload-documents';

@Component({
  selector: 'app-ia-filing-form',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink, UploadDocuments],
  templateUrl: './filing-form.html',
  styleUrl: './filing-form.css',
})
export class IaFilingForm implements OnInit {
  /** Mandatory IA court fee (matches backend `IA_COURT_FEE_AMOUNT`). */
  readonly iaCourtFeeRupees = 10;
  readonly iaPaymentType = 'IA Court Fee';

  form!: FormGroup;
  uploadFilingDocForm!: FormGroup;
  filings: any[] = [];
  filingsWithLitigants: Array<{ filing: any; litigants: any[] }> = [];
  searchQuery = '';
  isDropdownOpen = false;
  selectedFiling: any = null;
  caseDetails: any = null;
  litigants: any[] = [];
  acts: any[] = [];
  readonly litigantTypeOptions = EXISTING_CASE_LITIGANT_OPTIONS;
  litigantType: ExistingCaseLitigantType = 'PETITIONER';
  isLoadingFilings = true;
  isLoadingDetails = false;
  isUploadingDocuments = false;
  private isUploadRequestInFlight = false;
  isSubmitting = false;
  uploadFileProgresses: number[] = [];
  uploadCompletedToken = 0;

  docList: any[] = [];
  createdIa: any = null;
  isMergingPdf = false;
  mergeError: string | null = null;

  paymentOutcome: 'success' | 'failed' | null = null;
  paymentDetails: {
    txnId?: string;
    paidAt?: string;
    referenceNo?: string;
    amount?: string;
    paymentMode?: 'online' | 'offline';
    paymentDate?: string;
    bankReceipt?: string;
  } = {};
  paymentMode: 'online' | 'offline' = 'online';
  offlineTransactionId = '';
  offlineCourtFees: number | null = null;
  offlinePaymentDate = '';
  offlineBankReceipt: File | null = null;
  offlineBankReceiptName: string | null = null;
  isSubmittingOfflinePayment = false;

  constructor(
    private fb: FormBuilder,
    private efilingService: EfilingService,
    private paymentService: PaymentService,
    private router: Router,
    private route: ActivatedRoute,
    private toastr: ToastrService,
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      e_filing_id: ['', Validators.required],
      relief_sought: ['', Validators.required],
    });

    this.uploadFilingDocForm = this.fb.group({
      document_type: ['IA', Validators.required],
      final_document: [null],
    });

    this.route.queryParams.subscribe((params) => {
      this.applyIaPaymentReturnQueryParams(params);
    });

    this.offlineCourtFees = this.iaCourtFeeRupees;
    this.loadFilings();
  }

  iaFeeApplicationRef(): string | null {
    if (!this.createdIa?.id) return null;
    return `IA-FEE-${this.createdIa.id}`;
  }

  get requiresIaCourtFeePayment(): boolean {
    return !!this.createdIa?.id;
  }

  get isIaCourtFeePaid(): boolean {
    return this.paymentOutcome === 'success';
  }

  private applyIaPaymentReturnQueryParams(params: Params): void {
    const statusRaw =
      params['status'] ?? params['payment_status'] ?? params['txn_status'];
    if (statusRaw === undefined || statusRaw === null || statusRaw === '') {
      return;
    }
    const appParam = params['application'] ?? params['id'];
    const expected = this.iaFeeApplicationRef();
    if (expected && appParam !== undefined && String(appParam) !== String(expected)) {
      return;
    }
    const st = String(statusRaw).trim().toLowerCase();
    if (/(success|paid|complete|ok)/i.test(st)) {
      this.paymentOutcome = 'success';
    } else if (/(fail|reject|declin|error|cancel)/i.test(st)) {
      this.paymentOutcome = 'failed';
    } else {
      this.paymentOutcome = 'failed';
    }
    this.paymentDetails = {
      txnId:
        String(
          params['txn_id'] ??
            params['transaction_id'] ??
            params['sbs_ref_no'] ??
            '',
        ) || undefined,
      paidAt: String(params['payment_datetime'] ?? params['paid_at'] ?? '') || undefined,
      referenceNo: String(params['reference_no'] ?? '') || undefined,
      amount: String(params['amount'] ?? '') || undefined,
      paymentMode: 'online',
    };
    this.persistIaPaymentState();
    const clean: Record<string, string | number> = {};
    if (this.form.value.e_filing_id) {
      clean['e_filing_id'] = this.form.value.e_filing_id;
    }
    this.router.navigate([], { relativeTo: this.route, queryParams: clean, replaceUrl: true });
  }

  private persistIaPaymentState(): void {
    const key = this.iaPaymentStorageKey();
    if (!key || !this.paymentOutcome) return;
    try {
      sessionStorage.setItem(
        key,
        JSON.stringify({
          outcome: this.paymentOutcome,
          details: this.paymentDetails,
          at: Date.now(),
        }),
      );
    } catch {
      /* ignore */
    }
  }

  private restoreIaPaymentFromStorage(): void {
    const key = this.iaPaymentStorageKey();
    if (!key || this.paymentOutcome !== null) return;
    try {
      const raw = sessionStorage.getItem(key);
      if (!raw) return;
      const j = JSON.parse(raw) as {
        outcome?: string;
        details?: {
          txnId?: string;
          paidAt?: string;
          referenceNo?: string;
          amount?: string;
          paymentMode?: 'online' | 'offline';
          paymentDate?: string;
          bankReceipt?: string;
        };
      };
      if (j.outcome === 'success' || j.outcome === 'failed') {
        this.paymentOutcome = j.outcome;
        this.paymentDetails = j.details ?? {};
      }
    } catch {
      /* ignore */
    }
  }

  private iaPaymentStorageKey(): string | null {
    const id = this.createdIa?.id;
    if (!id) return null;
    return `ia_court_fee_${id}`;
  }

  async refreshIaPaymentStatusFromApi(): Promise<void> {
    const ref = this.iaFeeApplicationRef();
    if (!ref) return;
    try {
      const latest = await firstValueFrom(this.paymentService.latest(ref));
      const st = String(latest?.status ?? '').toLowerCase();
      if (/(success|paid|complete|ok)/i.test(st)) {
        this.paymentOutcome = 'success';
        this.paymentDetails = {
          txnId: latest.txn_id,
          referenceNo: latest.reference_no,
          amount: latest.amount ?? latest.court_fees,
          paidAt: latest.payment_datetime ?? latest.paid_at,
          paymentMode:
            latest.payment_mode === 'offline' ? 'offline' : 'online',
        };
        this.persistIaPaymentState();
      }
    } catch {
      /* ignore */
    }
  }

  confirmProceedToPayIaCourtFee(): void {
    const ref = this.iaFeeApplicationRef();
    const eFilingId = Number(this.form.value.e_filing_id);
    const selectedF = this.filings.find((f) => f.id === eFilingId);
    if (!ref || !selectedF?.e_filing_number) {
      this.toastr.warning('Complete at least one document upload so the IA record exists before paying the fee.');
      return;
    }
    this.paymentService
      .initiate({
        amount: this.iaCourtFeeRupees,
        application: ref,
        e_filing_number: selectedF.e_filing_number,
        payment_type: this.iaPaymentType,
        source: 'ia_filing',
      })
      .subscribe({
        next: (res) => {
          const form = document.createElement('form');
          form.method = res.method || 'POST';
          form.action = res.action;
          form.style.display = 'none';
          const fields = res.fields || {};
          Object.keys(fields).forEach((k) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = k;
            input.value = fields[k];
            form.appendChild(input);
          });
          document.body.appendChild(form);
          form.submit();
        },
        error: () => {
          this.toastr.error('Could not start payment. Try again later.');
        },
      });
  }

  onOfflineReceiptChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.offlineBankReceipt = file;
    this.offlineBankReceiptName = file ? file.name : null;
  }

  submitOfflineIaCourtFee(): void {
    const ref = this.iaFeeApplicationRef();
    const eFilingId = Number(this.form.value.e_filing_id);
    const selectedF = this.filings.find((f) => f.id === eFilingId);
    if (
      !ref ||
      !this.offlineTransactionId?.trim() ||
      !this.offlinePaymentDate ||
      !this.offlineBankReceipt ||
      !selectedF?.e_filing_number
    ) {
      this.toastr.warning('Fill bank receipt no., payment date, and upload receipt PDF.');
      return;
    }
    this.isSubmittingOfflinePayment = true;
    this.paymentService
      .submitOffline({
        application: ref,
        txn_id: this.offlineTransactionId.trim(),
        court_fees: this.iaCourtFeeRupees,
        payment_date: this.offlinePaymentDate,
        payment_type: this.iaPaymentType,
        e_filing_number: selectedF.e_filing_number,
        bank_receipt: this.offlineBankReceipt,
      })
      .subscribe({
        next: (res) => {
          this.isSubmittingOfflinePayment = false;
          this.paymentOutcome = 'success';
          this.paymentDetails = {
            txnId: res?.txn_id,
            referenceNo: res?.reference_no,
            paymentMode: 'offline',
            paymentDate: this.offlinePaymentDate,
            bankReceipt: res?.bank_receipt,
            amount: String(this.iaCourtFeeRupees),
          };
          this.persistIaPaymentState();
          this.toastr.success('Offline court fee recorded.');
        },
        error: (err) => {
          this.isSubmittingOfflinePayment = false;
          const msg = err?.error?.detail || err?.message || 'Failed to record offline payment.';
          this.toastr.error(msg);
        },
      });
  }

  private maxDocumentSequence(indexes: any[] | undefined): number {
    let max = 0;
    for (const x of indexes || []) {
      const s = Number(x?.document_sequence);
      if (Number.isFinite(s)) max = Math.max(max, s);
    }
    return max;
  }

  loadFilings(): void {
    this.isLoadingFilings = true;
    this.efilingService.get_filings().subscribe({
      next: (res) => {
        console.log(res);
        const rows = Array.isArray(res) ? res : res?.results ?? [];
        this.filings = rows.filter((f: any) => f?.id && f?.e_filing_number);
        this.loadLitigantsForFilings();
      },
      error: () => {
        this.filings = [];
        this.isLoadingFilings = false;
      },
    });
  }

  private loadLitigantsForFilings(): void {
    if (this.filings.length === 0) {
      this.filingsWithLitigants = [];
      this.isLoadingFilings = false;
      return;
    }
    const requests = this.filings.map((f) =>
      this.efilingService.get_litigant_list_by_filing_id(Number(f.id)),
    );
    forkJoin(requests).subscribe({
      next: (litigantResults) => {
        this.filingsWithLitigants = this.filings.map((filing, i) => {
          const list = Array.isArray(litigantResults[i])
            ? litigantResults[i]
            : litigantResults[i]?.results ?? [];
          return { filing, litigants: list };
        });
        this.isLoadingFilings = false;
      },
      error: () => {
        this.filingsWithLitigants = this.filings.map((f) => ({
          filing: f,
          litigants: [],
        }));
        this.isLoadingFilings = false;
      },
    });
  }

  get filteredFilingsWithLitigants(): Array<{ filing: any; litigants: any[] }> {
    const q = (this.searchQuery || '').trim().toLowerCase();
    if (!q) return this.filingsWithLitigants;
    return this.filingsWithLitigants.filter((item) => {
      const ef = (item.filing.e_filing_number || '').toLowerCase();
      const ct = (item.filing.case_type?.type_name || '').toLowerCase();
      const pn = (item.filing.petitioner_name || '').toLowerCase();
      const petNames = getOrderedPartyNames(item.litigants, true).join(' ').toLowerCase();
      const resNames = getOrderedPartyNames(item.litigants, false).join(' ').toLowerCase();
      const vsLine = this.getLitigantLabel(item).toLowerCase();
      return (
        ef.includes(q) ||
        ct.includes(q) ||
        pn.includes(q) ||
        petNames.includes(q) ||
        resNames.includes(q) ||
        vsLine.includes(q)
      );
    });
  }

  getLitigantLabel(item: { filing: any; litigants: any[] }): string {
    return (
      formatPetitionerVsRespondent(item.litigants, String(item.filing?.petitioner_name || '')) || '—'
    );
  }

  litigantTypeLabel(): string {
    const row = EXISTING_CASE_LITIGANT_OPTIONS.find((o) => o.value === this.litigantType);
    return row?.label ?? 'Petitioner';
  }

  litigantAnnexureLetter(): 'P' | 'A' | 'R' {
    const map: Record<ExistingCaseLitigantType, 'P' | 'A' | 'R'> = {
      PETITIONER: 'P',
      APPELLANT: 'A',
      RESPONDENT: 'R',
    };
    return map[this.litigantType] ?? 'P';
  }

  selectFiling(item: { filing: any }): void {
    this.form.patchValue({ e_filing_id: item.filing.id });
    this.createdIa = null;
    this.docList = [];
    this.paymentOutcome = null;
    this.paymentDetails = {};
    this.litigantType = 'PETITIONER';
    this.onFilingSelect();
    this.isDropdownOpen = false;
    this.searchQuery = '';
  }

  getSelectedLabel(): string {
    const id = this.form.value.e_filing_id;
    if (!id) return '';
    const item = this.filingsWithLitigants.find((x) => x.filing.id === Number(id));
    if (!item) return '';
    const f = item.filing;
    return `${f.e_filing_number} | ${f.case_type?.type_name || 'N/A'} | ${this.getLitigantLabel(item)}`;
  }

  onFilingSelect(): void {
    const id = this.form.value.e_filing_id;
    if (!id) {
      this.selectedFiling = null;
      this.caseDetails = null;
      this.litigants = [];
      this.acts = [];
      return;
    }

    this.isLoadingDetails = true;
    forkJoin({
      filing: this.efilingService.get_filing_by_id(Number(id)),
      caseDetails: this.efilingService.get_case_details_by_filing_id(Number(id)),
      litigants: this.efilingService.get_litigant_list_by_filing_id(Number(id)),
      acts: this.efilingService.get_acts_by_filing_id(Number(id)),
    }).subscribe({
      next: ({ filing, caseDetails, litigants, acts }) => {
        this.selectedFiling = filing;
        this.caseDetails = caseDetails?.results?.[0] ?? null;
        this.litigants = litigants?.results ?? [];
        this.acts = acts?.results ?? [];
        this.isLoadingDetails = false;
      },
      error: () => {
        this.selectedFiling = null;
        this.caseDetails = null;
        this.litigants = [];
        this.acts = [];
        this.isLoadingDetails = false;
      },
    });
  }

  get petitioners(): any[] {
    return this.litigants.filter((l) => l.is_petitioner);
  }

  get respondents(): any[] {
    return this.litigants.filter((l) => !l.is_petitioner);
  }

  getActName(act: any): string {
    return act?.act?.actname ?? act?.actname ?? '-';
  }

  trackLitigantById(_: number, litigant: any): number {
    return litigant?.id ?? 0;
  }

  async handleDocUpload(payload: any): Promise<void> {
    if (this.isUploadingDocuments || this.isUploadRequestInFlight) return;
    this.isUploadRequestInFlight = true;
    try {
      const documentType = String(payload?.document_type || '').trim();
      const uploadItems = Array.isArray(payload?.items) ? payload.items : [];
      const groupName = String(payload?.parent_group_name ?? '').trim();
      const eFilingId = Number(this.form.value.e_filing_id);
      const selectedF = this.filings.find((f) => f.id === eFilingId);
      const eFilingNumber = selectedF?.e_filing_number ?? '';
      const reliefSought = String(this.form.value.relief_sought || '').trim();

      if (!documentType || uploadItems.length === 0 || !eFilingId) {
        this.toastr.warning('Please select an E-Filing and add documents with index names.');
        return;
      }
      if (!groupName) {
        this.toastr.warning('Enter the parent Name (document group header) before uploading.');
        return;
      }
      if (!reliefSought) {
        this.toastr.warning('Please enter Relief Sought before uploading documents.');
        return;
      }

      // Validate PDF size (≤ 25 MB) and OCR before upload
      const files = uploadItems.map((i: any) => i.file).filter(Boolean);
      const { valid, errors } = validatePdfFiles(files);
      if (errors.length > 0) {
        this.toastr.error(errors.join(' '));
        return;
      }
      if (valid.length !== files.length) {
        this.toastr.error('Some files could not be validated. Please ensure all files are PDFs under 25 MB.');
        return;
      }
      const ocrError = await validatePdfOcrForFiles(valid);
      if (ocrError) {
        this.toastr.error(ocrError);
        return;
      }

      this.isUploadingDocuments = true;
      this.uploadFileProgresses = uploadItems.map(() => 0);

      if (!this.createdIa) {
        const iaRes = await firstValueFrom(
          this.efilingService.post_ia_filing({
            e_filing: eFilingId,
            e_filing_number: eFilingNumber,
            ia_text: reliefSought,
            status: 'DRAFT',
          }),
        );
        this.createdIa = iaRes;
        this.restoreIaPaymentFromStorage();
        void this.refreshIaPaymentStatusFromApi();
      }

      const iaNumber = this.createdIa?.ia_number ?? '';

      let documentRes = this.docList.find(
        (d) => String(d?.document_type || '').trim().toUpperCase() === 'IA',
      );
      let documentId = documentRes?.id;

      if (!documentId) {
        const documentPayload = new FormData();
        documentPayload.append('document_type', documentType);
        documentPayload.append('e_filing', String(eFilingId));
        documentPayload.append('e_filing_number', eFilingNumber);
        documentPayload.append('is_ia', 'true');
        documentPayload.append('ia_number', iaNumber);
        documentPayload.append('filed_by', this.litigantType);

        documentRes = await firstValueFrom(
          this.efilingService.upload_case_documnets(documentPayload),
        );
        documentId = documentRes?.id;
        if (!documentId) throw new Error('Document creation failed');
      }

      const existingIndexes = Array.isArray(documentRes?.document_indexes)
        ? documentRes.document_indexes
        : [];
      let nextSeq = this.maxDocumentSequence(existingIndexes);
      const uploadedParts: any[] = [];

      nextSeq += 1;
      const parentFd = new FormData();
      parentFd.append('document', String(documentId));
      parentFd.append('document_part_name', groupName);
      parentFd.append('document_sequence', String(nextSeq));
      const parentRes = await firstValueFrom(
        this.efilingService.createDocumentIndexMetadata(parentFd),
      );
      const parentIndexId =
        parentRes?.id != null ? Number(parentRes.id) : null;
      if (parentRes) uploadedParts.push(parentRes);

      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];
        nextSeq += 1;
        const indexPayload = new FormData();
        indexPayload.append('document', String(documentId));
        indexPayload.append('document_part_name', String(item.index_name || '').trim());
        indexPayload.append('file_part_path', item.file);
        indexPayload.append('document_sequence', String(nextSeq));
        if (item.index_id) indexPayload.append('index', String(item.index_id));
        if (parentIndexId != null) {
          indexPayload.append('parent_document_index', String(parentIndexId));
        }

        const partRes = await this.uploadIndexWithProgress(indexPayload, i);
        uploadedParts.push(partRes);
      }

      const mergedIndexes = [...existingIndexes, ...uploadedParts];
      const firstWithFile = mergedIndexes.find(
        (p: any) => p?.file_url || p?.file_part_path,
      );
      const mergedDoc = {
        ...documentRes,
        document_type: documentType,
        document_indexes: mergedIndexes,
        final_document:
          firstWithFile?.file_url ||
          firstWithFile?.file_part_path ||
          documentRes?.final_document,
      };

      const existingIdx = this.docList.findIndex((d) => Number(d?.id) === Number(documentId));
      if (existingIdx > -1) {
        this.docList[existingIdx] = mergedDoc;
      } else {
        this.docList.push(mergedDoc);
      }
      this.uploadCompletedToken++;
      this.toastr.success('Documents uploaded successfully.');
    } catch (err) {
      console.error('Document upload failed', err);
      const msg = getValidationErrorMessage(err);
      const friendlyMsg =
        !msg || /bad request|http error|400/i.test(msg)
          ? 'Failed to upload documents. Please ensure all PDFs are under 25 MB and OCR-converted (searchable).'
          : msg;
      this.toastr.error(friendlyMsg);
    } finally {
      this.isUploadingDocuments = false;
      this.isUploadRequestInFlight = false;
    }
  }

  private uploadIndexWithProgress(formData: FormData, index: number): Promise<any> {
    return new Promise((resolve, reject) => {
      this.efilingService.upload_case_documnets_index(formData).subscribe({
        next: (event: any) => {
          if (event.type === HttpEventType.UploadProgress && event.total) {
            this.uploadFileProgresses[index] = Math.round((event.loaded / event.total) * 100);
          }
          if (event.type === HttpEventType.Response) {
            this.uploadFileProgresses[index] = 100;
            resolve(event.body);
          }
        },
        error: (err) => reject(err),
      });
    });
  }

  async onSubmit(): Promise<void> {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    if (this.isSubmitting) return;

    if (!this.createdIa?.id) {
      this.toastr.warning('Upload at least one document set before final submission.');
      return;
    }
    if (this.docList.length === 0) {
      this.toastr.warning('Upload documents before submitting.');
      return;
    }

    await this.refreshIaPaymentStatusFromApi();
    if (!this.isIaCourtFeePaid) {
      this.toastr.error(
        `Pay the mandatory court fee of Rs. ${this.iaCourtFeeRupees}/- before submitting this IA.`,
      );
      return;
    }

    const proceed = await this.promptOtpAndProceed(
      'Submit IA Filing?',
      'Once submitted, this IA filing will be forwarded for scrutiny.',
    );
    if (!proceed) return;

    const reliefSought = String(this.form.value.relief_sought || '').trim();

    this.isSubmitting = true;

    this.efilingService.patch_ia_filing(this.createdIa.id, {
      status: 'UNDER_SCRUTINY',
      ia_text: reliefSought,
    }).subscribe({
      next: () => {
        try {
          const key = this.iaPaymentStorageKey();
          if (key) sessionStorage.removeItem(key);
        } catch {
          /* ignore */
        }
        this.toastr.success('IA Filing submitted successfully.');
        this.router.navigate(['/advocate/dashboard/efiling/ia-filing/view']);
        this.isSubmitting = false;
      },
      error: (err) => {
        this.isSubmitting = false;
        console.error('IA filing submit failed', err);
        const body = err?.error;
        let msg: string | null = null;
        if (body && typeof body === 'object') {
          const st = (body as any).status;
          if (Array.isArray(st) && st.length) msg = String(st[0]);
          else if (typeof st === 'string') msg = st;
        }
        if (!msg && body?.detail) msg = String(body.detail);
        if (!msg) msg = err?.message || 'Failed to submit IA filing.';
        this.toastr.error(msg ?? 'Failed to submit IA filing.');
      },
    });
  }

  private async promptOtpAndProceed(title: string, text: string): Promise<boolean> {
    const confirmed = await Swal.fire({
      title,
      text,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Yes, Submit',
      cancelButtonText: 'Cancel',
    });
    if (!confirmed.isConfirmed) return false;

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

  deleteDoc(id: number, index: number): void {
    const confirmDelete = confirm(
      'Your document will be deleted and you need to re-upload it. Continue?',
    );
    if (!confirmDelete) return;

    this.efilingService.delete_case_documnets_before_final_filing(id).subscribe({
      next: () => {
        this.docList.splice(index, 1);
        this.toastr.success('Document deleted.');
      },
      error: () => {
        this.toastr.error('Failed to delete document.');
      },
    });
  }

  private getMergeItems(): { url: string; name: string }[] {
    const items: { url: string; name: string }[] = [];
    const list = Array.isArray(this.docList) ? this.docList : [];
    for (const doc of list) {
      const indexes = doc?.document_indexes;
      if (Array.isArray(indexes) && indexes.length > 0) {
        for (const part of indexes) {
          const url = part?.file_url || part?.file_part_path;
          if (url) {
            const name = part?.document_part_name?.trim() || doc?.document_type || 'Document';
            items.push({ url, name });
          }
        }
      } else if (doc?.final_document) {
        const url = doc.final_document;
        const name = doc?.document_type?.trim() || 'Document';
        items.push({ url, name });
      }
    }
    return items;
  }

  private toAbsoluteUrl(url: string): string {
    if (!url) return '';
    const s = String(url).trim();
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    const base = app_url.replace(/\/$/, '');
    return s.startsWith('/') ? `${base}${s}` : `${base}/${s}`;
  }

  canDownloadMerged(): boolean {
    return this.getMergeItems().length > 0;
  }

  downloadMergedPdf(): void {
    const items = this.getMergeItems();
    if (items.length === 0 || this.isMergingPdf) return;

    this.isMergingPdf = true;
    this.mergeError = null;

    const fetches = items.map((item) =>
      this.efilingService.fetch_document_blob(this.toAbsoluteUrl(item.url)),
    );

    forkJoin(fetches).subscribe({
      next: (blobs) => {
        const files = blobs.map((blob, i) => {
          const name = items[i].name.replace(/\.pdf$/i, '') + '.pdf';
          return new File([blob], name, { type: 'application/pdf' });
        });
        const names = items.map((i) => i.name);
        const init = this.selectedFiling || {};
        const caseType = init?.case_type?.full_form || init?.case_type?.type_name || '';
        const pnFallback = String(init.petitioner_name || '').trim();
        const frontPage = {
          petitionerName: formatPartyLine(getOrderedPartyNames(this.litigants, true), pnFallback),
          respondentName: formatPartyLine(getOrderedPartyNames(this.litigants, false), ''),
          caseNo: (init.e_filing_number || '').trim(),
          caseType,
        };

        this.efilingService.mergePdfs(files, names, frontPage).subscribe({
          next: (mergedBlob) => {
            const url = URL.createObjectURL(mergedBlob);
            const a = document.createElement('a');
            a.href = url;
            const docType = (this.docList?.[0]?.document_type || 'IA').replace(/[^a-zA-Z0-9_-]/g, '_') || 'IA';
            const iaNo = (this.createdIa?.ia_number || this.selectedFiling?.e_filing_number || '').replace(/[^a-zA-Z0-9_-]/g, '') || 'merged';
            a.download = `${docType}_${iaNo}.pdf`;
            a.click();
            URL.revokeObjectURL(url);
            this.isMergingPdf = false;
          },
          error: (err) => {
            this.isMergingPdf = false;
            this.mergeError = err?.error?.error || err?.message || 'Failed to merge PDFs.';
          },
        });
      },
      error: () => {
        this.isMergingPdf = false;
        this.mergeError = 'Failed to fetch documents.';
      },
    });
  }

  trackById(_: number, item: any): number {
    return item?.id ?? 0;
  }

  trackFilingItem(_: number, item: { filing: any }): number {
    return item?.filing?.id ?? 0;
  }
}
