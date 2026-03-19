import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
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

  entries: DocumentUploadEntry[] = [];
  indexMasters: DocumentIndexMaster[] = [];

  constructor(private eFilingService: EfilingService) {}

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

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const selectedEntries: DocumentUploadEntry[] = Array.from(input.files)
      .filter((file) => file.type === 'application/pdf')
      .map((file) => ({
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

  canUpload(): boolean {
    return (
      !this.isUploading &&
      this.entries.length > 0 &&
      !!String(this.form.value.document_type || '').trim() &&
      this.entries.every((entry) => entry.index_name && entry.index_name.trim().length > 0)
    );
  }

  submit() {
    if (!this.canUpload()) return;

    const payload: UploadDocumentsPayload = {
      document_type: String(this.form.value.document_type || '').trim(),
      items: this.entries.map((entry) => ({
        file: entry.file,
        index_name: entry.index_name.trim(),
        index_id: entry.index_id,
      })),
    };

    this.submitDoc.emit(payload);
  }

  getFileProgress(index: number): number {
    const progress = this.fileProgresses?.[index];
    if (typeof progress !== 'number') return 0;
    return Math.min(100, Math.max(0, Math.round(progress)));
  }

  hasAnyProgress(): boolean {
    return (this.fileProgresses || []).some((p) => typeof p === 'number' && p > 0);
  }
}
