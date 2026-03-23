import { CommonModule } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
} from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
import { validatePdfFiles } from '../../../../../../utils/pdf-validation';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';

interface DocumentUploadEntry {
  file: File;
  index_name: string;
  index_id: number | null;
}

interface DocumentIndexMaster {
  id: number;
  name: string;
}

interface UploadDocumentsPayloadItem {
  file: File;
  index_name: string;
  index_id: number | null;
}

interface UploadDocumentsPayload {
  document_type: string;
  items: UploadDocumentsPayloadItem[];
}

@Component({
  selector: 'app-upload-documents',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, DragDropModule],
  templateUrl: './upload-documents.html',
  styleUrl: './upload-documents.css',
})
export class UploadDocuments implements OnInit, OnChanges {
  @Output() submitDoc = new EventEmitter<UploadDocumentsPayload>();
  @Input() form!: FormGroup;
  @Input() isUploading = false;
  @Input() fileProgresses: number[] = [];
  @Input() uploadCompletedToken = 0;
  /** When set, hides the document type field and uses this value (e.g. 'IA' for IA filing). */
  @Input() defaultDocumentType: string | null = null;
  /** Optional front page data for merged PDF (petitioner vs respondent, case no, case type). */
  @Input() frontPage: { petitionerName: string; respondentName: string; caseNo: string; caseType?: string } | null = null;
  /** E-Filing number for merged PDF filename (e.g. DocumentType_efilingno.pdf). */
  @Input() eFilingNumber: string | null = null;

  entries: DocumentUploadEntry[] = [];
  indexMasters: DocumentIndexMaster[] = [];
  submitAttempted = false;
  isMerging = false;
  mergeError: string | null = null;

  constructor(
    private eFilingService: EfilingService,
    private toastr: ToastrService,
  ) {}

  ngOnInit(): void {
    this.eFilingService.get_document_index_master().subscribe({
      next: (res) => {
        const rows = Array.isArray(res) ? res : Array.isArray(res?.results) ? res.results : [];
        this.indexMasters = rows
          .map((item: any) => ({
            id: Number(item?.id),
            name: String(item?.name ?? '').trim(),
          }))
          .filter((item: DocumentIndexMaster) => Number.isFinite(item.id) && !!item.name);
      },
      error: () => {
        this.indexMasters = [];
      },
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['uploadCompletedToken'] && !changes['uploadCompletedToken'].firstChange) {
      this.form.reset();
      this.entries = [];
    }
  }

  onTopDocumentTypeInput(value: string) {
    this.form.patchValue({ document_type: value });
  }

  isDocumentTypeInvalid(): boolean {
    const control = this.form?.get('document_type');
    return !!control && control.invalid && (control.touched || control.dirty);
  }

  isFilesInvalid(): boolean {
    return this.submitAttempted && this.entries.length === 0;
  }

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const files = Array.from(input.files);
    const { valid, errors } = validatePdfFiles(files);
    if (errors.length > 0) {
      this.toastr.error(errors.join(' '));
    }
    if (valid.length === 0) return;

    const selectedEntries: DocumentUploadEntry[] = valid.map((file) => ({
      file,
      index_name: '',
      index_id: null,
    }));

    this.entries = [...this.entries, ...selectedEntries];

    this.form.patchValue({
      final_document: this.entries.length > 0 ? this.entries[0].file : null,
    });

    input.value = '';
  }

  updateDocumentType(index: number, value: string) {
    const entry = this.entries[index];
    if (!entry) return;
    const typedValue = value;
    entry.index_name = typedValue;

    const normalized = typedValue.trim().toLowerCase();
    const matchedMaster = this.indexMasters.find((item) => item.name.toLowerCase() === normalized);
    entry.index_id = matchedMaster ? matchedMaster.id : null;
  }

  getIndexSuggestions(query: string): string[] {
    const q = (query || '').trim().toLowerCase();
    if (!q) return [];

    return this.indexMasters
      .map((item) => item.name)
      .filter((name) => name.toLowerCase().includes(q))
      .slice(0, 12);
  }

  trackByEntry(index: number, entry: DocumentUploadEntry): File {
    return entry.file;
  }

  removeEntry(index: number) {
    this.entries = this.entries.filter((_, i) => i !== index);

    this.form.patchValue({
      final_document: this.entries.length > 0 ? this.entries[0].file : null,
    });
  }

  reorderEntries(event: CdkDragDrop<DocumentUploadEntry[]>) {
    if (this.isUploading) return;
    moveItemInArray(this.entries, event.previousIndex, event.currentIndex);
  }

  getEffectiveDocumentType(): string {
    if (this.defaultDocumentType) {
      return String(this.defaultDocumentType).trim();
    }
    return String(this.form?.value?.document_type || '').trim();
  }

  canUpload(): boolean {
    return (
      !this.isUploading &&
      this.entries.length > 0 &&
      !!this.getEffectiveDocumentType() &&
      this.entries.every((entry) => entry.index_name && entry.index_name.trim().length > 0)
    );
  }

  submit() {
    this.submitAttempted = true;
    if (!this.canUpload()) return;

    const payload: UploadDocumentsPayload = {
      document_type: this.getEffectiveDocumentType(),
      items: this.entries.map((entry) => ({
        file: entry.file,
        index_name: entry.index_name.trim(),
        index_id: entry.index_id,
      })),
    };
    // console.log(payload);
    this.submitDoc.emit(payload);
    this.submitAttempted = false;
  }

  isIndexNameInvalid(entry: DocumentUploadEntry): boolean {
    if (!this.submitAttempted) return false;
    return !entry.index_name || entry.index_name.trim().length === 0;
  }

  getFileProgress(index: number): number {
    const progress = this.fileProgresses?.[index];
    if (typeof progress !== 'number') return 0;
    return Math.min(100, Math.max(0, Math.round(progress)));
  }

  hasAnyProgress(): boolean {
    return (this.fileProgresses || []).some((p) => typeof p === 'number' && p > 0);
  }

  canDownloadMerged(): boolean {
    return (
      !this.isUploading &&
      !this.isMerging &&
      this.entries.length > 0 &&
      this.entries.every((e) => e.index_name && e.index_name.trim().length > 0)
    );
  }

  downloadMergedPdf(): void {
    if (!this.canDownloadMerged()) return;
    const files = this.entries.map((e) => e.file);
    const names = this.entries.map((e) => e.index_name.trim());
    const frontPage = this.frontPage
      ? {
          petitionerName: this.frontPage.petitionerName || '',
          respondentName: this.frontPage.respondentName || '',
          caseNo: this.frontPage.caseNo || '',
          caseType: this.frontPage.caseType || '',
        }
      : undefined;
    this.isMerging = true;
    this.mergeError = null;
    this.eFilingService.mergePdfs(files, names, frontPage).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const docType = (this.getEffectiveDocumentType() || 'Documents').replace(/[^a-zA-Z0-9_-]/g, '_') || 'Documents';
        const efilingNo = (this.eFilingNumber || '').replace(/[^a-zA-Z0-9_-]/g, '') || 'merged';
        a.download = `${docType}_${efilingNo}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
        this.isMerging = false;
      },
      error: (err) => {
        this.isMerging = false;
        const msg =
          (typeof err?.error === 'object' && err?.error !== null && typeof err.error.error === 'string'
            ? err.error.error
            : null) ||
          err?.message ||
          'Failed to merge PDFs.';
        this.mergeError = msg;
      },
    });
  }
}
