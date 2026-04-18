import { CommonModule } from '@angular/common';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subject } from 'rxjs';

import { CourtroomService } from '../../../../services/judge/courtroom.service';
import { PdfAnnotatorComponent } from '../../../judges/dashboard/courtroom/pdf-annotator.component';
import { buildCollapsedDisplaySections, DocumentDisplaySection, orderDocumentsForDisplay } from '../../../../shared/document-groups';

@Component({
  selector: 'app-advocate-courtview',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, PdfAnnotatorComponent],
  templateUrl: './advocate-courtview.html',
  styleUrl: './advocate-courtview.css',
})
export class AdvocateCourtviewPage implements OnInit, OnDestroy {
  efilingId: number | null = null;
  forwardedForDate: string | null = null;

  isLoading = false;
  loadError = '';

  caseSummary: any = null;
  allCaseDocuments: any[] = [];
  
  previewDocument: any = null;
  previewDocumentBlobUrl: string | null = null;
  previewLoadError = '';

  documentSearchQuery: string = '';

  isSharing = false;
  currentPageIndex = 0;

  private destroy$ = new Subject<void>();
  private expandedVakalatGroupIds = new Set<string>();
  private expandedOrdersGroupIds = new Set<string>();

  constructor(
    private route: ActivatedRoute,
    private courtroomService: CourtroomService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const idRaw = this.route.snapshot.paramMap.get('id');
    this.efilingId = idRaw ? Number(idRaw) : null;
    this.forwardedForDate = this.route.snapshot.queryParamMap.get('forwarded_for_date');
    if (!this.forwardedForDate) {
        this.forwardedForDate = new Date().toISOString().split('T')[0];
    }
    
    if (!this.efilingId) {
      this.loadError = 'Missing case id.';
      return;
    }

    this.loadCaseSummary();
  }

  ngOnDestroy(): void {
    if (this.isSharing && this.efilingId) {
       this.courtroomService.stopSharedView(this.efilingId).subscribe();
    }
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadCaseSummary(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.isLoading = true;
    this.courtroomService.getCaseSummary(this.efilingId, this.forwardedForDate).subscribe({
      next: (resp) => {
        this.caseSummary = resp ?? null;
        this.loadCaseDocuments();
        this.isLoading = false;
      },
      error: () => {
        this.loadError = 'Failed to load case details.';
        this.isLoading = false;
      },
    });
  }

  private loadCaseDocuments(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.courtroomService.getCaseDocuments(this.efilingId, this.forwardedForDate, null ,false).subscribe({
      next: (resp) => {
        this.allCaseDocuments = resp?.items ?? [];
        if (this.allCaseDocuments.length && !this.previewDocument) {
          this.selectPreviewDocument(this.allCaseDocuments[0]);
        }
      },
      error: () => {
        this.allCaseDocuments = [];
      },
    });
  }

  selectPreviewDocument(doc: any): void {
    const newId = Number(doc?.id);
    const prevId = Number(this.previewDocument?.id);
    if (newId !== prevId) {
      this.currentPageIndex = 0;
    }
    this.previewDocument = doc;
    this.updatePreviewUrl(doc ?? null);
  }

  /** After PDF renders in the annotator; broadcast so judge follow gets correct doc + page 1. */
  onPdfReady(): void {
    this.currentPageIndex = 0;
    if (this.isSharing) {
      this.broadcastPosition();
    }
  }

  private updatePreviewUrl(document: any | null): void {
    if (this.previewDocumentBlobUrl) {
      URL.revokeObjectURL(this.previewDocumentBlobUrl);
      this.previewDocumentBlobUrl = null;
    }
    const docId = Number(document?.id || 0);
    const fileUrl = document?.file_url || document?.file_part_path || null;
    if (!docId && !fileUrl) return;

    const resolvedUrl = fileUrl ? this.courtroomService.resolveDocumentUrl(fileUrl) : '';
    const stream$ = docId
      ? this.courtroomService.fetchDocumentBlobByIndex(docId)
      : this.courtroomService.fetchDocumentBlob(resolvedUrl);

    stream$.subscribe({
      next: (blob) => {
        this.previewDocumentBlobUrl = URL.createObjectURL(blob);
      },
      error: () => {
        this.previewLoadError = 'Unable to load PDF preview.';
      },
    });
  }

  toggleSharing() {
    this.isSharing = !this.isSharing;
    if (this.isSharing) {
       this.broadcastPosition();
    } else if (this.efilingId) {
       this.courtroomService.stopSharedView(this.efilingId).subscribe();
    }
  }

  onPageChange(pageIndex: number) {
     this.currentPageIndex = pageIndex;
     if (this.isSharing) {
        this.broadcastPosition();
     }
  }

  private broadcastPosition() {
    if (!this.efilingId || !this.previewDocument || !this.isSharing) return;
    this.courtroomService.updateSharedView({
        efiling_id: this.efilingId,
        document_index_id: this.previewDocument.id,
        page_index: this.currentPageIndex
    }).subscribe();
  }

  get filteredCaseDocuments(): any[] {
    return orderDocumentsForDisplay(this.allCaseDocuments, this.documentSearchQuery);
  }

  get documentDisplaySections(): DocumentDisplaySection[] {
    return buildCollapsedDisplaySections(this.filteredCaseDocuments);
  }

  publishedOrderLabel(doc: any): string | null {
    const raw = doc?.published_order_at;
    if (!raw) return null;
    try {
      const d = new Date(raw);
      if (Number.isNaN(d.getTime())) return null;
      return `Published: ${d.toLocaleString()}`;
    } catch {
      return null;
    }
  }

  isVakalatGroupExpanded(id: string): boolean {
    return this.expandedVakalatGroupIds.has(id);
  }

  toggleVakalatGroup(id: string): void {
    if (this.expandedVakalatGroupIds.has(id)) {
      this.expandedVakalatGroupIds.delete(id);
      return;
    }
    this.expandedVakalatGroupIds.add(id);
  }

  isOrdersGroupExpanded(id: string): boolean {
    return this.expandedOrdersGroupIds.has(id);
  }

  toggleOrdersGroup(id: string): void {
    if (this.expandedOrdersGroupIds.has(id)) {
      this.expandedOrdersGroupIds.delete(id);
      return;
    }
    this.expandedOrdersGroupIds.add(id);
  }

  get petitionerNamesLabel(): string {
    const parts = (this.caseSummary?.petitioner_vs_respondent || '').split(/v\/s/i);
    return (parts[0] || '').trim() || 'Petitioner';
  }

  get respondentNamesLabel(): string {
    const parts = (this.caseSummary?.petitioner_vs_respondent || '').split(/v\/s/i);
    return parts.length > 1 ? (parts[1] || '').trim() : 'Respondent';
  }
}
