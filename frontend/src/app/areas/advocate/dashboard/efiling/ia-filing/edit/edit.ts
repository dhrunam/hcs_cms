import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-ia-filing-edit',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './edit.html',
  styleUrl: './edit.css',
})
export class IaFilingEdit implements OnInit {
  ia: any = null;
  filing: any = null;
  caseDetails: any = null;
  litigants: any[] = [];
  acts: any[] = [];
  iaActs: any[] = [];
  documents: any[] = [];
  groupedDocuments: Array<{ document_type: string; items: any[] }> = [];
  selectedDocument: any = null;
  selectedDocumentUrl: SafeResourceUrl | null = null;
  selectedDocumentBlobUrl: string | null = null;
  isLoading = true;
  notFound = false;
  activeTab: 'filing' | 'documents' = 'filing';

  constructor(
    private route: ActivatedRoute,
    private efilingService: EfilingService,
    private sanitizer: DomSanitizer,
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.notFound = true;
      this.isLoading = false;
      return;
    }

    this.efilingService.get_ia_by_id(Number(id)).subscribe({
      next: (ia) => {
        this.ia = ia;
        const eFilingId = ia?.e_filing;
        if (eFilingId) {
          forkJoin({
            filing: this.efilingService.get_filing_by_id(Number(eFilingId)),
            caseDetails: this.efilingService.get_case_details_by_filing_id(Number(eFilingId)),
            litigants: this.efilingService.get_litigant_list_by_filing_id(Number(eFilingId)),
            acts: this.efilingService.get_acts_by_filing_id(Number(eFilingId)),
            // iaActs: this.efilingService.get_ia_acts_by_ia_id(Number(id)),
            documents: this.efilingService.get_document_reviews_by_filing_id(Number(eFilingId)),
          }).subscribe({
            next: ({ filing, caseDetails, litigants, acts, documents }) => {
              this.filing = filing;
              this.caseDetails = caseDetails?.results?.[0] ?? null;
              this.litigants = Array.isArray(litigants) ? litigants : litigants?.results ?? [];
              this.acts = Array.isArray(acts) ? acts : acts?.results ?? [];
              // this.iaActs = Array.isArray(iaActs) ? iaActs : iaActs?.results ?? [];
              this.documents = Array.isArray(documents) ? documents : documents?.results ?? [];
              this.groupedDocuments = this.groupDocumentsByType(this.documents);
              this.selectDocument(this.documents[0] ?? null);
              this.isLoading = false;
            },
            error: () => {
              this.isLoading = false;
            },
          });
        } else {
          this.isLoading = false;
        }
      },
      error: () => {
        this.notFound = true;
        this.isLoading = false;
      },
    });
  }

  setActiveTab(tab: 'filing' | 'documents'): void {
    this.activeTab = tab;
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

  groupDocumentsByType(docs: any[]): Array<{ document_type: string; items: any[] }> {
    if (!Array.isArray(docs) || docs.length === 0) return [];
    const map = new Map<string, any[]>();
    for (const doc of docs) {
      const type = (doc?.document_type ?? '').trim() || 'Main Document';
      const bucket = map.get(type);
      if (bucket) {
        bucket.push(doc);
      } else {
        map.set(type, [doc]);
      }
    }
    return Array.from(map.entries()).map(([document_type, items]) => ({ document_type, items }));
  }

  selectDocument(document: any): void {
    this.selectedDocument = document;
    this.updatePreviewUrl(document?.file_url ?? null);
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

  trackById(_: number, item: any): number {
    return item?.id ?? 0;
  }

  trackByGroupIndex(_: number, group: { document_type: string; items: any[] }): string {
    return group.document_type;
  }
}
