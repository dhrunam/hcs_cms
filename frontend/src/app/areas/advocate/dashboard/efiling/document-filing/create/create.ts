import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { HttpEventType } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { CaseTypeService } from '../../../../../../services/master/case-type.services';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
import { UploadDocuments } from '../../new-filing/upload-documents/upload-documents';

@Component({
  selector: 'app-create',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, UploadDocuments],
  templateUrl: './create.html',
  styleUrl: './create.css',
})
export class Create {
  searchForm!: FormGroup;
  caseTypes: any[] = [];

  isSearching = false;
  searchMatches: any[] = [];
  selectedFiling: any = null;

  isLoadingCase = false;
  caseDetails: any = null;
  docList: any[] = [];

  // UploadDocuments inputs
  isUploadingDocuments = false;
  uploadFileProgresses: number[] = [];
  uploadCompletedToken = 0;
  uploadFilingDocForm!: FormGroup;

  // Store for upload API calls
  selectedEfilingId: number | null = null;
  selectedEfilingNumber: string = '';

  constructor(
    private fb: FormBuilder,
    private caseTypeService: CaseTypeService,
    private eFilingService: EfilingService,
  ) {
    this.searchForm = this.fb.group({
      case_type: ['', Validators.required],
      case_no: ['', Validators.required],
      case_year: ['', Validators.required],
    });

    this.uploadFilingDocForm = this.fb.group({
      document_type: [null, Validators.required],
      final_document: [[], Validators.required],
    });
  }

  ngOnInit(): void {
    this.caseTypeService.get_case_types().subscribe({
      next: (data) => {
        this.caseTypes = data?.results ?? data ?? [];
      },
      error: () => {
        this.caseTypes = [];
      },
    });
  }

  private normalizeNumber(value: string): string {
    const trimmed = String(value ?? '').trim();
    if (!trimmed) return '';
    const noLeadingZeros = trimmed.replace(/^0+/, '');
    return noLeadingZeros === '' ? '0' : noLeadingZeros;
  }

  private parseEfilingNumber(efilingNumber: string): { year: string; seq7: string; seq5: string } | null {
    const raw = String(efilingNumber ?? '');
    // Example: ASK2024{seq7}C{year}{seq5}
    const m = raw.match(/^ASK\d{4}(\d{7})C(\d{4})(\d{5})/);
    if (!m) return null;
    return { seq7: m[1], year: m[2], seq5: m[3] };
  }

  private efilingMatchesCase(
    efiling: any,
    caseTypeId: number,
    caseNo: string,
    caseYear: string,
  ): boolean {
    if (!efiling) return false;

    const filingCaseTypeId = efiling?.case_type?.id;
    if (!filingCaseTypeId || Number(filingCaseTypeId) !== Number(caseTypeId)) return false;

    const parsed = this.parseEfilingNumber(efiling?.e_filing_number);
    if (!parsed) return false;

    const inputYear = String(caseYear ?? '').trim();
    if (!inputYear || parsed.year !== inputYear) return false;

    const inputNoNorm = this.normalizeNumber(caseNo);
    if (!inputNoNorm) return false;

    const seq7Norm = this.normalizeNumber(parsed.seq7);
    const seq5Norm = this.normalizeNumber(parsed.seq5);

    return seq7Norm === inputNoNorm || seq5Norm === inputNoNorm;
  }

  searchCase(): void {
    if (this.searchForm.invalid) return;

    const { case_type, case_no, case_year } = this.searchForm.value;
    const caseTypeId = Number(case_type);
    const inputCaseNo = String(case_no ?? '');
    const inputYear = String(case_year ?? '');

    this.isSearching = true;
    this.searchMatches = [];
    this.selectedFiling = null;
    this.docList = [];
    this.caseDetails = null;

    forkJoin({
      draft: this.eFilingService.get_filings_under_draft(),
      scrutiny: this.eFilingService.get_filings_under_scrutiny(),
    }).subscribe({
      next: ({ draft, scrutiny }) => {
        const draftRows = draft?.results ?? [];
        const scrutinyRows = scrutiny?.results ?? [];
        const merged = [...draftRows, ...scrutinyRows];

        this.searchMatches = merged.filter((f: any) =>
          this.efilingMatchesCase(f, caseTypeId, inputCaseNo, inputYear),
        );

        if (this.searchMatches.length === 1) {
          this.selectFiling(this.searchMatches[0]);
        }

        this.isSearching = false;
      },
      error: () => {
        this.isSearching = false;
        this.searchMatches = [];
      },
    });
  }

  selectFiling(efiling: any): void {
    if (!efiling?.id) return;

    this.selectedFiling = efiling;
    this.selectedEfilingId = efiling.id;
    this.selectedEfilingNumber = String(efiling.e_filing_number ?? '');

    this.loadSelectedCaseDetailsAndDocs();
  }

  private loadSelectedCaseDetailsAndDocs(): void {
    if (!this.selectedEfilingId) return;

    this.isLoadingCase = true;
    this.caseDetails = null;
    this.docList = [];

    forkJoin({
      caseDetails: this.eFilingService.get_case_details_by_filing_id(this.selectedEfilingId),
      documents: this.eFilingService.get_documents_by_filing_id(this.selectedEfilingId),
      documentIndexes: this.eFilingService.get_document_reviews_by_filing_id(this.selectedEfilingId),
    }).subscribe({
      next: ({ caseDetails, documents, documentIndexes }) => {
        const caseRows = caseDetails?.results ?? [];
        this.caseDetails = caseRows?.[0] ?? null;

        const mainDocs = documents?.results ?? [];
        const indexParts = documentIndexes?.results ?? [];

        // Build docList as: main document + its index parts grouped by document id
        this.docList = mainDocs.map((doc: any) => {
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
      },
    });
  }

  trackByEfilingId(_: number, item: any): number {
    return item?.id;
  }

  trackByDocId(_: number, item: any): number {
    return item?.id;
  }

  openUploadDocumentsEnabled(): boolean {
    return Boolean(this.selectedEfilingId);
  }

  async handleDocUpload(data: any): Promise<void> {
    const documentType = String(data?.document_type || '').trim();
    const uploadItems = Array.isArray(data?.items) ? data.items : [];

    if (!documentType || uploadItems.length === 0 || !this.selectedEfilingId) return;

    this.isUploadingDocuments = true;
    this.uploadFileProgresses = uploadItems.map(() => 0);

    try {
      const documentPayload = new FormData();
      documentPayload.append('document_type', documentType);
      documentPayload.append('e_filing', String(this.selectedEfilingId));
      documentPayload.append('e_filing_number', this.selectedEfilingNumber);

      const documentRes = await firstValueFrom(this.eFilingService.upload_case_documnets(documentPayload));
      const documentId = documentRes?.id;
      if (!documentId) return;

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

      this.docList.push({
        ...documentRes,
        document_indexes: uploadedDocumentParts,
        final_document: uploadedDocumentParts[0]?.file_url || documentRes?.final_document,
      });

      this.uploadCompletedToken++;
    } catch (error) {
      console.error('Document upload failed', error);
    } finally {
      this.isUploadingDocuments = false;
    }
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

