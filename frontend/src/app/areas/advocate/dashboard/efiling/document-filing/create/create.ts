import { CommonModule } from '@angular/common';
import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { forkJoin } from 'rxjs';
import { ToastrService } from 'ngx-toastr';
import Swal from 'sweetalert2';

import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
import { UploadDocuments } from '../../new-filing/upload-documents/upload-documents';

@Component({
  selector: 'app-document-filing-create',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink, UploadDocuments],
  templateUrl: './create.html',
  styleUrl: './create.css',
})
export class Create implements OnInit {
  uploadFilingDocForm!: FormGroup;

  filings: any[] = [];
  filingsWithLitigants: Array<{ filing: any; petitioners: string[]; respondents: string[] }> = [];
  searchQuery = '';
  isDropdownOpen = false;
  selectedFiling: any = null;

  isLoadingFilings = true;
  isLoadingCase = false;
  caseDetails: any = null;

  existingDocList: any[] = [];
  uploadedDocList: any[] = [];

  isUploadingDocuments = false;
  uploadFileProgresses: number[] = [];
  uploadCompletedToken = 0;

  selectedEfilingId: number | null = null;
  selectedEfilingNumber = '';

  constructor(
    private fb: FormBuilder,
    private eFilingService: EfilingService,
    private toastr: ToastrService,
  ) {
    this.uploadFilingDocForm = this.fb.group({
      document_type: ['', Validators.required],
      final_document: [null],
    });
  }

  ngOnInit(): void {
    this.loadFilings();
  }

  loadFilings(): void {
    this.isLoadingFilings = true;
    forkJoin({
      draft: this.eFilingService.get_filings_under_draft(),
      scrutiny: this.eFilingService.get_filings_under_scrutiny(),
    }).subscribe({
      next: ({ draft, scrutiny }) => {
        const draftRows = draft?.results ?? [];
        const scrutinyRows = scrutiny?.results ?? [];
        const merged = [...draftRows, ...scrutinyRows];
        this.filings = merged.filter((f: any) => f?.id && f?.e_filing_number);
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
      this.eFilingService.get_litigant_list_by_filing_id(Number(f.id)),
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
      return ef.includes(q) || ct.includes(q) || pn.includes(q) || petNames.includes(q) || resNames.includes(q);
    });
  }

  getLitigantLabel(item: { filing: any; petitioners: string[]; respondents: string[] }): string {
    const p = item.petitioners.filter(Boolean).join(', ') || item.filing?.petitioner_name || '-';
    const r = item.respondents.filter(Boolean).join(', ') || '-';
    return `${p} vs ${r}`;
  }

  selectFiling(item: { filing: any }): void {
    this.selectedFiling = item.filing;
    this.selectedEfilingId = item.filing.id;
    this.selectedEfilingNumber = String(item.filing.e_filing_number ?? '');
    this.isDropdownOpen = false;
    this.searchQuery = '';
    this.uploadedDocList = [];
    this.loadSelectedCaseDetailsAndDocs();
  }

  getSelectedLabel(): string {
    if (!this.selectedFiling) return '';
    const item = this.filingsWithLitigants.find((x) => x.filing.id === this.selectedFiling.id);
    if (!item) return `${this.selectedFiling.e_filing_number} | ${this.selectedFiling.case_type?.type_name || 'N/A'}`;
    return `${this.selectedFiling.e_filing_number} | ${this.selectedFiling.case_type?.type_name || 'N/A'} | ${this.getLitigantLabel(item)}`;
  }

  private loadSelectedCaseDetailsAndDocs(): void {
    if (!this.selectedEfilingId) return;

    this.isLoadingCase = true;
    this.caseDetails = null;
    this.existingDocList = [];

    forkJoin({
      caseDetails: this.eFilingService.get_case_details_by_filing_id(this.selectedEfilingId),
      documents: this.eFilingService.get_documents_by_filing_id(this.selectedEfilingId),
      documentIndexes: this.eFilingService.get_document_reviews_by_filing_id(this.selectedEfilingId, false),
    }).subscribe({
      next: ({ caseDetails, documents, documentIndexes }) => {
        const caseRows = caseDetails?.results ?? [];
        this.caseDetails = caseRows?.[0] ?? null;

        const mainDocs = documents?.results ?? [];
        const indexParts = documentIndexes?.results ?? [];

        this.existingDocList = mainDocs.map((doc: any) => {
          const partsForDoc = indexParts
            .filter((p: any) => Number(p.document) === Number(doc.id))
            .sort((a: any, b: any) => Number(a.document_sequence) - Number(b.document_sequence));

          return {
            ...doc,
            document_indexes: partsForDoc,
          };
        });

        this.isLoadingCase = false;
      },
      error: () => {
        this.isLoadingCase = false;
        this.toastr.error('Failed to load case details.');
      },
    });
  }

  deleteDoc(id: number, index: number): void {
    const confirmDelete = confirm(
      'Your document will be deleted and you need to re-upload it. Continue?',
    );
    if (!confirmDelete) return;

    this.eFilingService.delete_case_documnets_before_final_filing(id).subscribe({
      next: () => {
        this.uploadedDocList.splice(index, 1);
        this.toastr.success('Document deleted.');
      },
      error: () => {
        this.toastr.error('Failed to delete document.');
      },
    });
  }

  trackByDocId(_: number, item: any): number {
    return item?.id ?? 0;
  }

  trackFilingItem(_: number, item: { filing: any }): number {
    return item?.filing?.id ?? 0;
  }

  private isDocumentVerified(doc: any): boolean {
    const indexes = doc?.document_indexes ?? [];
    if (indexes.length === 0) return false;
    return indexes.every((p: any) => {
      const s = (p?.scrutiny_status ?? '').trim().toLowerCase();
      return s.includes('accept');
    });
  }

  get verifiedDocList(): any[] {
    return this.existingDocList.filter((doc) => this.isDocumentVerified(doc));
  }

  get nonVerifiedDocList(): any[] {
    return this.existingDocList.filter((doc) => !this.isDocumentVerified(doc));
  }

  async handleDocUpload(data: any): Promise<void> {
    const documentType = String(data?.document_type || '').trim();
    const uploadItems = Array.isArray(data?.items) ? data.items : [];

    if (!documentType || uploadItems.length === 0 || !this.selectedEfilingId) {
      this.toastr.warning('Please select an E-Filing and add documents with document type and index names.');
      return;
    }

    const proceed = await this.promptOtpAndProceed('File Documents?', 'Upload these documents to the selected case.');
    if (!proceed) return;

    this.isUploadingDocuments = true;
    this.uploadFileProgresses = uploadItems.map(() => 0);

    try {
      const documentPayload = new FormData();
      documentPayload.append('document_type', documentType);
      documentPayload.append('e_filing', String(this.selectedEfilingId));
      documentPayload.append('e_filing_number', this.selectedEfilingNumber);

      const documentRes = await firstValueFrom(this.eFilingService.upload_case_documnets(documentPayload));
      const documentId = documentRes?.id;
      if (!documentId) throw new Error('Document creation failed');

      const uploadedDocumentParts: any[] = [];

      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];
        const indexPayload = new FormData();
        indexPayload.append('document', String(documentId));
        indexPayload.append('document_part_name', String(item.index_name || '').trim());
        indexPayload.append('file_part_path', item.file);
        indexPayload.append('document_sequence', String(i + 1));
        if (item.index_id) {
          indexPayload.append('index', String(item.index_id));
        }

        const indexRes = await this.uploadIndexFileWithProgress(indexPayload, i);
        uploadedDocumentParts.push(indexRes);
      }

      this.uploadedDocList.push({
        ...documentRes,
        document_indexes: uploadedDocumentParts,
        final_document: uploadedDocumentParts[0]?.file_url || documentRes?.final_document,
      });

      this.uploadCompletedToken++;
      this.toastr.success('Documents uploaded successfully.');
    } catch (error) {
      console.error('Document upload failed', error);
      this.toastr.error('Failed to upload documents. Please try again.');
    } finally {
      this.isUploadingDocuments = false;
    }
  }

  private async promptOtpAndProceed(title: string, text: string): Promise<boolean> {
    const confirmed = await Swal.fire({
      title,
      text,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Yes, Proceed',
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

  private uploadIndexFileWithProgress(formData: FormData, index: number): Promise<any> {
    return new Promise((resolve, reject) => {
      this.eFilingService.upload_case_documnets_index(formData).subscribe({
        next: (event: any) => {
          if (event.type === HttpEventType.UploadProgress) {
            const total = event.total || 0;
            if (total > 0) {
              this.uploadFileProgresses[index] = Math.round((event.loaded / total) * 100);
            }
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
}
