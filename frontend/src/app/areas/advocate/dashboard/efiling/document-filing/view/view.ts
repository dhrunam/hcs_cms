import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-document-filing-view',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class View implements OnInit {
  documents: any[] = [];
  groupedByEfiling: Array<{ efilingId: number; efilingNumber: string; docs: any[] }> = [];
  isLoading = true;

  constructor(private eFilingService: EfilingService) {}

  ngOnInit(): void {
    this.eFilingService.get_efiling_documents().subscribe({
      next: (res) => {
        const rows = Array.isArray(res) ? res : res?.results ?? [];
        this.documents = rows;

        const map = new Map<number, { efilingNumber: string; docs: any[] }>();
        for (const doc of this.documents) {
          const efilingId = doc.e_filing ?? doc.e_filing_id;
          if (efilingId == null) continue;
          const id = Number(efilingId);
          const existing = map.get(id);
          const efilingNumber = doc.e_filing_number || '-';
          if (existing) {
            existing.docs.push(doc);
          } else {
            map.set(id, { efilingNumber, docs: [doc] });
          }
        }

        this.groupedByEfiling = Array.from(map.entries()).map(([efilingId, data]) => ({
          efilingId,
          efilingNumber: data.efilingNumber,
          docs: data.docs,
        }));

        this.isLoading = false;
      },
      error: () => {
        this.documents = [];
        this.groupedByEfiling = [];
        this.isLoading = false;
      },
    });
  }

  trackByEfilingId(_: number, item: { efilingId: number }): number {
    return item.efilingId;
  }

  trackByDocId(_: number, item: any): number {
    return item?.id ?? 0;
  }
}
