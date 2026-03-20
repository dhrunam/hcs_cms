import { CommonModule } from '@angular/common';
import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { forkJoin } from 'rxjs';
import { ToastrService } from 'ngx-toastr';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
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
      document_type: ['', Validators.required],
      final_document: [null],
    });

    this.loadFilings();
  }

  loadFilings(): void {
    this.isLoadingFilings = true;
    this.efilingService.get_filings_under_scrutiny().subscribe({
      next: (res) => {
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

  async handleDocUpload(payload: any): Promise<void> {
    const documentType = String(payload?.document_type || '').trim();
    const uploadItems = Array.isArray(payload?.items) ? payload.items : [];
    const eFilingId = Number(this.form.value.e_filing_id);
    const selectedF = this.filings.find((f) => f.id === eFilingId);
    const eFilingNumber = selectedF?.e_filing_number ?? '';

    if (!documentType || uploadItems.length === 0 || !eFilingId) {
      this.toastr.warning('Please select an E-Filing and add documents with document type and index names.');
      return;
    }

    this.isUploadingDocuments = true;
    this.uploadFileProgresses = uploadItems.map(() => 0);

    try {
      const documentPayload = new FormData();
      documentPayload.append('document_type', documentType);
      documentPayload.append('e_filing', String(eFilingId));
      documentPayload.append('e_filing_number', eFilingNumber);

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
      this.toastr.error('Failed to upload documents. Please try again.');
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

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    if (this.isSubmitting) return;

    const eFilingId = Number(this.form.value.e_filing_id);
    const selectedF = this.filings.find((f) => f.id === eFilingId);
    const eFilingNumber = selectedF?.e_filing_number ?? '';
    const reliefSought = String(this.form.value.relief_sought || '').trim();

    this.isSubmitting = true;
    this.efilingService
      .post_ia_filing({
        e_filing: eFilingId,
        e_filing_number: eFilingNumber,
        ia_text: reliefSought,
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

  trackById(_: number, item: any): number {
    return item?.id ?? 0;
  }

  trackFilingItem(_: number, item: { filing: any }): number {
    return item?.filing?.id ?? 0;
  }
}
