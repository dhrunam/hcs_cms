import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';

export interface DocumentFilingGroup {
  efilingId: number;
  efilingNumber: string;
  docs: any[];
  petitionerVsRespondent: string;
}

@Component({
  selector: 'app-document-filing-view',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class DocumentFilingView implements OnInit {
  isLoading = true;
  groupedByEfiling: DocumentFilingGroup[] = [];

  constructor(private eFilingService: EfilingService) {}

  ngOnInit(): void {
    this.load();
  }

  private load(): void {
    this.isLoading = true;
    forkJoin({
      docs: this.eFilingService.get_efiling_documents(),
      filings: this.eFilingService.get_filings(),
    }).subscribe({
      next: ({ docs, filings }) => {
        const docRows = Array.isArray(docs?.results) ? docs.results : Array.isArray(docs) ? docs : [];
        const filingRows = Array.isArray(filings?.results) ? filings.results : Array.isArray(filings) ? filings : [];
        const byId = new Map<number, any>();
        for (const f of filingRows) {
          const id = Number(f?.id);
          if (Number.isFinite(id) && id > 0) byId.set(id, f);
        }
        const map = new Map<number, any[]>();
        for (const d of docRows) {
          const efId = Number(d?.e_filing);
          if (!Number.isFinite(efId) || efId <= 0) continue;
          const list = map.get(efId) ?? [];
          list.push(d);
          map.set(efId, list);
        }
        this.groupedByEfiling = [...map.entries()]
          .map(([efilingId, groupDocs]) => {
            const f = byId.get(efilingId);
            const line = String(f?.petitioner_vs_respondent || '').trim();
            return {
              efilingId,
              efilingNumber: String(f?.e_filing_number ?? groupDocs[0]?.e_filing_number ?? ''),
              docs: groupDocs,
              petitionerVsRespondent: line,
            };
          })
          .sort((a, b) => (a.efilingNumber || '').localeCompare(b.efilingNumber || ''));
        this.isLoading = false;
      },
      error: () => {
        this.groupedByEfiling = [];
        this.isLoading = false;
      },
    });
  }

  trackByEfilingId(_: number, g: DocumentFilingGroup): number {
    return g.efilingId;
  }
}
