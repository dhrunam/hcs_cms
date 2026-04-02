import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import Swal from 'sweetalert2';

import { CourtroomService } from '../../../../services/judge/courtroom.service';
import { benchLabel } from '../../../listing-officers/shared/bench-labels';
import { PdfAnnotatorComponent } from '../courtroom/pdf-annotator.component';

@Component({
  selector: 'app-judge-courtview-case',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, PdfAnnotatorComponent],
  templateUrl: './courtview-case.html',
  styleUrl: './courtview-case.css',
})
export class JudgeCourtviewCasePage implements OnInit {
  benchLabel = benchLabel;
  efilingId: number | null = null;
  forwardedForDate: string | null = null;

  isLoading = false;
  loadError = '';

  caseSummary: any = null;
  allCaseDocuments: any[] = [];
  
  previewDocument: any = null;
  previewDocumentBlobUrl: string | null = null;
  previewLoadError = '';

  canWrite = false;

  constructor(
    private route: ActivatedRoute,
    private courtroomService: CourtroomService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.canWrite = true; 

    // Date is fixed essentially to today since we removed picker, but we still pick it up from query param 
    // to strictly identify the correct forward row.
    const idRaw = this.route.snapshot.paramMap.get('id');
    this.efilingId = idRaw ? Number(idRaw) : null;
    this.forwardedForDate = this.route.snapshot.queryParamMap.get('forwarded_for_date');
    
    if (!this.efilingId || !this.forwardedForDate) {
      this.loadError = 'Missing case id or forwarded_for_date.';
      return;
    }

    this.loadCaseSummary();
  }

  private loadCaseSummary(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.isLoading = true;
    this.loadError = '';

    this.courtroomService.getCaseSummary(this.efilingId, this.forwardedForDate).subscribe({
      next: (resp) => {
        this.caseSummary = resp ?? null;
        this.forwardedForDate = resp?.forwarded_for_date ?? this.forwardedForDate;
        this.loadCaseDocuments();
        this.isLoading = false;
      },
      error: (err) => {
        console.warn('Failed to load case summary', err);
        this.loadError = 'Failed to load case details.';
        this.isLoading = false;
      },
    });
  }

  private loadCaseDocuments(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.courtroomService.getCaseDocuments(this.efilingId, this.forwardedForDate, false).subscribe({
      next: (resp) => {
        this.allCaseDocuments = resp?.items ?? [];
        if (this.allCaseDocuments.length && !this.previewDocument) {
          this.selectPreviewDocument(this.allCaseDocuments[0]);
        }
      },
      error: (err) => {
        console.warn('Failed to load case documents', err);
        this.allCaseDocuments = [];
      },
    });
  }

  selectPreviewDocument(doc: any): void {
    this.previewDocument = doc;
    this.updatePreviewUrl(doc ?? null);
  }

  private updatePreviewUrl(document: any | null): void {
    if (this.previewDocumentBlobUrl) {
      URL.revokeObjectURL(this.previewDocumentBlobUrl);
      this.previewDocumentBlobUrl = null;
    }
    const docId = Number(document?.id || 0);
    const fileUrl = document?.file_url || document?.file_part_path || null;
    if (!docId && !fileUrl) {
      this.previewLoadError = '';
      return;
    }
    const resolvedUrl = fileUrl ? this.courtroomService.resolveDocumentUrl(fileUrl) : '';
    this.previewLoadError = '';
    
    const stream$ = docId
      ? this.courtroomService.fetchDocumentBlobByIndex(docId)
      : this.courtroomService.fetchDocumentBlob(resolvedUrl);

    stream$.subscribe({
      next: (blob) => {
        this.previewDocumentBlobUrl = URL.createObjectURL(blob);
      },
      error: () => {
        this.previewLoadError = 'Unable to load PDF preview (file missing or moved).';
      },
    });
  }

  onSaveAnnotations(payload: any) {
    if (!this.previewDocument || !this.canWrite) return;
    this.courtroomService.saveDocumentAnnotation({
      efiling_document_index_id: this.previewDocument.id,
      annotation_data: payload
    }).subscribe({
      next: (res) => {
        this.previewDocument.annotation_data = res.annotation_data;
        Swal.fire({
          title: 'Saved',
          icon: 'success',
          timer: 1200,
          showConfirmButton: false,
          toast: true,
          position: 'top-end'
        });
      },
      error: () => {
        Swal.fire({
          title: 'Error',
          text: 'Failed to save annotations.',
          icon: 'error'
        });
      }
    });
  }

  get petitionerNamesLabel(): string {
    if (this.caseSummary?.petitioner_name) return this.caseSummary.petitioner_name;
    const parts = (this.caseSummary?.petitioner_vs_respondent || '').split(/v\/s/i);
    return (parts[0] || '').trim() || 'Petitioner';
  }

  get respondentNamesLabel(): string {
    if (this.caseSummary?.respondent_name) return this.caseSummary.respondent_name;
    const parts = (this.caseSummary?.petitioner_vs_respondent || '').split(/v\/s/i);
    return parts.length > 1 ? (parts[1] || '').trim() : 'Respondent';
  }
}
