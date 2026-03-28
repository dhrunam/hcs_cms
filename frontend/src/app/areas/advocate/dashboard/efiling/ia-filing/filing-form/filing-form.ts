import { CommonModule } from '@angular/common';
import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { forkJoin } from 'rxjs';
import { ToastrService } from 'ngx-toastr';
import Swal from 'sweetalert2';
import { app_url } from '../../../../../../environment';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
import {
  getValidationErrorMessage,
  validatePdfFiles,
  validatePdfOcrForFiles,
} from '../../../../../../utils/pdf-validation';
import { UploadDocuments } from '../../new-filing/upload-documents/upload-documents';

@Component({
  selector: 'app-ia-filing-form',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink, UploadDocuments],
  templateUrl: './filing-form.html',
  styleUrl: './filing-form.css',
})
export class IaFilingForm implements OnInit {
  form!: FormGroup;
  uploadFilingDocForm!: FormGroup;
  filings: any[] = [];
  filingsWithLitigants: Array<{ filing: any; petitioners: string[]; respondents: string[] }> = [];
  searchQuery = '';
  isDropdownOpen = false;
  selectedFiling: any = null;
  caseDetails: any = null;
  litigants: any[] = [];
  acts: any[] = [];
  isLoadingFilings = true;
  isLoadingDetails = false;
  isUploadingDocuments = false;
  isSubmitting = false;
  uploadFileProgresses: number[] = [];
  uploadCompletedToken = 0;

  docList: any[] = [];
  createdIa: any = null;
  isMergingPdf = false;
  mergeError: string | null = null;

  constructor(
    private fb: FormBuilder,
    private efilingService: EfilingService,
    private router: Router,
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

    this.loadFilings();
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
          const petitioners = list.filter((l: any) => l.is_petitioner).map((l: any) => l.name || '');
          const respondents = list.filter((l: any) => !l.is_petitioner).map((l: any) => l.name || '');
          return { filing, petitioners, respondents };
        });
        this.isLoadingFilings = false;
      },
      error: () => {
        this.filingsWithLitigants = this.filings.map((f) => ({
          filing: f,
          petitioners: [],
          respondents: [],
        }));
        this.isLoadingFilings = false;
      },
    });
  }

  get filteredFilingsWithLitigants(): Array<{ filing: any; petitioners: string[]; respondents: string[] }> {
    const q = (this.searchQuery || '').trim().toLowerCase();
    if (!q) return this.filingsWithLitigants;
    return this.filingsWithLitigants.filter((item) => {
      const ef = (item.filing.e_filing_number || '').toLowerCase();
      const ct = (item.filing.case_type?.type_name || '').toLowerCase();
      const pn = (item.filing.petitioner_name || '').toLowerCase();
      const petNames = item.petitioners.join(' ').toLowerCase();
      const resNames = item.respondents.join(' ').toLowerCase();
      const vs = `${petNames} vs ${resNames}`.toLowerCase();
      return ef.includes(q) || ct.includes(q) || pn.includes(q) || petNames.includes(q) || resNames.includes(q) || vs.includes(q);
    });
  }

  getLitigantLabel(item: { filing: any; petitioners: string[]; respondents: string[] }): string {
    const p = item.petitioners.filter(Boolean).join(', ') || item.filing?.petitioner_name || '-';
    const r = item.respondents.filter(Boolean).join(', ') || '-';
    return `${p} vs ${r}`;
  }

  selectFiling(item: { filing: any }): void {
    this.form.patchValue({ e_filing_id: item.filing.id });
    this.createdIa = null;
    this.docList = [];
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
    const documentType = String(payload?.document_type || '').trim();
    const uploadItems = Array.isArray(payload?.items) ? payload.items : [];
    const eFilingId = Number(this.form.value.e_filing_id);
    const selectedF = this.filings.find((f) => f.id === eFilingId);
    const eFilingNumber = selectedF?.e_filing_number ?? '';
    const reliefSought = String(this.form.value.relief_sought || '').trim();

    if (!documentType || uploadItems.length === 0 || !eFilingId) {
      this.toastr.warning('Please select an E-Filing and add documents with index names.');
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

    try {
      if (!this.createdIa) {
        const iaRes = await firstValueFrom(
          this.efilingService.post_ia_filing({
            e_filing: eFilingId,
            e_filing_number: eFilingNumber,
            ia_text: reliefSought,
            status: 'UNDER_SCRUTINY',
          }),
        );
        this.createdIa = iaRes;
      }

      const iaNumber = this.createdIa?.ia_number ?? '';

      const documentPayload = new FormData();
      documentPayload.append('document_type', documentType);
      documentPayload.append('e_filing', String(eFilingId));
      documentPayload.append('e_filing_number', eFilingNumber);
      documentPayload.append('is_ia', 'true');
      documentPayload.append('ia_number', iaNumber);

      const documentRes = await firstValueFrom(
        this.efilingService.upload_case_documnets(documentPayload),
      );

      const documentId = documentRes?.id;
      if (!documentId) throw new Error('Document creation failed');

      const uploadedParts: any[] = [];
      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];
        const indexPayload = new FormData();
        indexPayload.append('document', String(documentId));
        indexPayload.append('document_part_name', String(item.index_name || '').trim());
        indexPayload.append('file_part_path', item.file);
        indexPayload.append('document_sequence', String(i + 1));
        if (item.index_id) indexPayload.append('index', String(item.index_id));

        const partRes = await this.uploadIndexWithProgress(indexPayload, i);
        uploadedParts.push(partRes);
      }

      this.docList.push({
        ...documentRes,
        document_indexes: uploadedParts,
        final_document: uploadedParts[0]?.file_url || documentRes?.final_document,
      });
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

    const proceed = await this.promptOtpAndProceed(
      'Submit IA Filing?',
      'Once submitted, this IA filing will be forwarded for scrutiny.',
    );
    if (!proceed) return;

    const eFilingId = Number(this.form.value.e_filing_id);
    const selectedF = this.filings.find((f) => f.id === eFilingId);
    const eFilingNumber = selectedF?.e_filing_number ?? '';
    const reliefSought = String(this.form.value.relief_sought || '').trim();

    this.isSubmitting = true;

    if (this.createdIa) {
      this.toastr.success('IA Filing submitted successfully.');
      this.router.navigate(['/advocate/dashboard/efiling/ia-filing/view']);
      this.isSubmitting = false;
      return;
    }

    this.efilingService
      .post_ia_filing({
        e_filing: eFilingId,
        e_filing_number: eFilingNumber,
        ia_text: reliefSought,
        status: 'UNDER_SCRUTINY',
      })
      .subscribe({
        next: () => {
          this.toastr.success('IA Filing submitted successfully.');
          this.router.navigate(['/advocate/dashboard/efiling/ia-filing/view']);
        },
        error: (err) => {
          this.isSubmitting = false;
          console.error('IA filing submit failed', err);
          const msg = err?.error?.detail || err?.error?.message || err?.message || 'Failed to submit IA filing.';
          this.toastr.error(msg);
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
        const petitionerNames = (this.petitioners || [])
          .map((l: any) => l.name || '')
          .filter(Boolean)
          .join(', ');
        const respondentNames = (this.respondents || [])
          .map((l: any) => l.name || '')
          .filter(Boolean)
          .join(', ');
        const init = this.selectedFiling || {};
        const caseType = init?.case_type?.full_form || init?.case_type?.type_name || '';
        const frontPage = {
          petitionerName: (init.petitioner_name || '').trim() || petitionerNames,
          respondentName: respondentNames,
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
