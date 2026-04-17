import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { catchError, forkJoin, of } from 'rxjs';
import { EfilingService } from '../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-scrutiny-officer-menus',
  imports: [CommonModule, RouterModule],
  templateUrl: './scrutiny-officer-menus.html',
  styleUrl: './scrutiny-officer-menus.css',
})
export class ScrutinyOfficerMenus {
  pendingCaseAccessCount = 0;
  registeredCaseNewCount = 0;
  private pollTimer: ReturnType<typeof setInterval> | null = null;

  constructor(private efilingService: EfilingService) {}

  ngOnInit(): void {
    this.loadPendingCaseAccessCount();
    this.loadRegisteredCaseNewCount();
    this.pollTimer = setInterval(() => {
      this.loadPendingCaseAccessCount();
      this.loadRegisteredCaseNewCount();
    }, 30000);
  }

  ngOnDestroy(): void {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  private loadPendingCaseAccessCount(): void {
    this.efilingService.get_case_access_requests('PENDING').subscribe({
      next: (payload) => {
        if (Array.isArray(payload)) {
          this.pendingCaseAccessCount = payload.length;
          return;
        }
        const results = Array.isArray(payload?.results) ? payload.results : [];
        this.pendingCaseAccessCount = results.length;
      },
      error: () => {
        this.pendingCaseAccessCount = 0;
      },
    });
  }

  private loadRegisteredCaseNewCount(): void {
    const pageSize = 9999;
    forkJoin({
      filings: this.efilingService.get_scrutiny_cases({ page_size: pageSize }),
      incoming: this.efilingService.get_new_scrutiny_documents({ page_size: pageSize }).pipe(
        catchError(() => of([])),
      ),
    }).subscribe({
      next: ({ filings, incoming }) => {
        const allFilings = Array.isArray((filings as any)?.results)
          ? (filings as any).results
          : Array.isArray(filings)
            ? filings
            : [];
        const registeredIdSet = new Set<number>(
          allFilings
            .filter((f: any) => !!String(f?.case_number || '').trim())
            .map((f: any) => Number(f?.id))
            .filter((id: number) => Number.isFinite(id)),
        );
        const incomingRows = Array.isArray((incoming as any)?.results)
          ? (incoming as any).results
          : Array.isArray(incoming)
            ? incoming
            : [];
        const matched = new Set<number>();
        for (const row of incomingRows) {
          const eFilingId = Number(row?.e_filing_id);
          if (Number.isFinite(eFilingId) && registeredIdSet.has(eFilingId)) {
            matched.add(eFilingId);
          }
        }
        this.registeredCaseNewCount = matched.size;
      },
      error: () => {
        this.registeredCaseNewCount = 0;
      },
    });
  }
}
