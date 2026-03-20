import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-document-filing-edit',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './edit.html',
  styleUrl: './edit.css',
})
export class Edit implements OnInit {
  filing: any = null;
  caseDetails: any = null;
  docList: any[] = [];
  isLoading = true;
  notFound = false;

  constructor(
    private route: ActivatedRoute,
    private eFilingService: EfilingService,
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.notFound = true;
      this.isLoading = false;
      return;
    }

    const efilingId = Number(id);
    forkJoin({
      filing: this.eFilingService.get_filing_by_id(efilingId),
      caseDetails: this.eFilingService.get_case_details_by_filing_id(efilingId),
      documents: this.eFilingService.get_documents_by_filing_id(efilingId),
      documentIndexes: this.eFilingService.get_document_reviews_by_filing_id(efilingId),
    }).subscribe({
      next: ({ filing, caseDetails, documents, documentIndexes }) => {
        this.filing = filing;
        const caseRows = caseDetails?.results ?? [];
        this.caseDetails = caseRows?.[0] ?? null;

        const mainDocs = documents?.results ?? [];
        const indexParts = documentIndexes?.results ?? [];

        this.docList = mainDocs.map((doc: any) => {
          const partsForDoc = indexParts
            .filter((p: any) => Number(p.document) === Number(doc.id))
            .sort((a: any, b: any) => Number(a.document_sequence) - Number(b.document_sequence));

          return {
            ...doc,
            document_indexes: partsForDoc,
          };
        });

        this.isLoading = false;
      },
      error: () => {
        this.notFound = true;
        this.isLoading = false;
      },
    });
  }

  trackByDocId(_: number, item: any): number {
    return item?.id ?? 0;
  }
}
