import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { catchError, forkJoin, of } from 'rxjs';
import { EfilingService } from '../../../../services/advocate/efiling/efiling.services';

interface EfilingCaseType {
  type_name?: string;
}

interface EfilingItem {
  id: number;
  petitioner_name: string;
  petitioner_contact: string;
  e_filing_number: string;
  case_number?: string | null;
  accepted_at?: string | null;
  created_at: string;
  status: string | null;
  case_type: EfilingCaseType | null;
}

@Component({
  selector: 'app-scrutiny-officer-home',
  imports: [CommonModule, RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class ScrutinyOfficerHome {
  filedCases: EfilingItem[] = [];
  newIncomingFilingIds = new Set<number>();
  isLoading = false;

  constructor(private eFilingService: EfilingService) {}

  ngOnInit(): void {
    this.getFiledCases();
  }

  get totalFiledCases(): number {
    return this.openFiledCases.length;
  }

  get totalRegisteredCases(): number {
    return this.registeredCases.length;
  }

  get newIncomingCount(): number {
    return this.newIncomingFilingIds.size;
  }

  get underScrutinyCount(): number {
    return this.openFiledCases.filter((item) => this.getStatusTone(item.status) === 'warning').length;
  }

  get acceptedCount(): number {
    return this.filedCases.filter((item) => this.getStatusTone(item.status) === 'success').length;
  }

  get rejectedCount(): number {
    return this.openFiledCases.filter((item) => this.getStatusTone(item.status) === 'danger').length;
  }

  get dashboardPreviewCases(): EfilingItem[] {
    return this.openFiledCases.slice(0, 10);
  }

  get registeredCasesPreview(): EfilingItem[] {
    return this.registeredCases.slice(0, 5);
  }

  get openFiledCases(): EfilingItem[] {
    return this.filedCases.filter((item) => !item.case_number);
  }

  get registeredCases(): EfilingItem[] {
    return this.filedCases.filter((item) => !!item.case_number);
  }

  getFiledCases(): void {
    this.isLoading = true;
    forkJoin({
      filings: this.eFilingService.get_filings_under_scrutiny(),
      incoming: this.eFilingService.get_new_scrutiny_documents().pipe(
        catchError((error) => {
          console.warn('Failed to load new scrutiny documents', error);
          return of([]);
        }),
      ),
    }).subscribe({
      next: ({ filings, incoming }) => {
        this.filedCases = this.extractItems(filings);
        this.newIncomingFilingIds = new Set<number>(
          this.extractItems(incoming)
            .map((item: any) => item?.e_filing_id)
            .filter((id: number | null | undefined) => typeof id === 'number'),
        );
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load filed cases', error);
        this.filedCases = [];
        this.newIncomingFilingIds = new Set<number>();
        this.isLoading = false;
      },
    });
  }

  private extractItems(payload: any): any[] {
    if (Array.isArray(payload)) {
      return payload;
    }
    if (Array.isArray(payload?.results)) {
      return payload.results;
    }
    return [];
  }

  hasNewForScrutiny(filingId: number | null | undefined): boolean {
    return typeof filingId === 'number' && this.newIncomingFilingIds.has(filingId);
  }

  getStatusLabel(status: string | null): string {
    const normalizedStatus = (status ?? '').trim().toLowerCase();

    if (!normalizedStatus || normalizedStatus === 'submitted' || normalizedStatus === 'under_scrutiny') {
      return 'Under Scrutiny';
    }

    if (normalizedStatus.includes('accept')) {
      return 'Accepted';
    }

    if (normalizedStatus.includes('partially')) {
      return 'Partially Rejected';
    }

    if (
      normalizedStatus.includes('reject') ||
      normalizedStatus.includes('object') ||
      normalizedStatus.includes('defect')
    ) {
      return 'Rejected';
    }

    return status ?? 'Under Scrutiny';
  }

  getStatusTone(status: string | null): 'warning' | 'success' | 'danger' {
    const label = this.getStatusLabel(status).toLowerCase();

    if (label.includes('accept')) {
      return 'success';
    }

    if (label.includes('partial') || label.includes('reject') || label.includes('defect')) {
      return 'danger';
    }

    return 'warning';
  }
}
