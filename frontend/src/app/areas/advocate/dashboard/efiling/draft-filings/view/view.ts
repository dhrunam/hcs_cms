import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
interface PendingCase {
  id: number;
  caseTitle: string;
  filingType: string;
  filedOn: string;
  status: string;
}

@Component({
  selector: 'app-view',
  imports: [CommonModule, RouterLink],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class View {
  filingsUnderDraft: any[] | null = null;

  constructor(private eFilingService: EfilingService) {}

  getStatusLabel(status: string | null): string {
    const s = (status ?? 'draft').trim().toLowerCase();
    if (!s || s === 'draft') return 'Draft';
    if (s.includes('accept')) return 'Accepted';
    if (s.includes('reject') || s.includes('partial')) return s.includes('partial') ? 'Partially Rejected' : 'Rejected';
    if (s.includes('scrutiny') || s.includes('submitted')) return 'Under Scrutiny';
    return status ?? 'Draft';
  }

  getStatusBadgeClass(status: string | null): string {
    const label = this.getStatusLabel(status).toLowerCase();
    if (label.includes('accept')) return 'status-badge-success';
    if (label.includes('reject') || label.includes('partial')) return 'status-badge-danger';
    return 'status-badge-warning';
  }

  ngOnInit() {
    this.get_filings_under_scrutiny();
  }

  get_filings_under_scrutiny() {
    this.eFilingService.get_filings_under_draft().subscribe({
      next: (data) => {
        this.filingsUnderDraft = data.results;
        console.log(this.filingsUnderDraft);
      },
    });
  }
}
