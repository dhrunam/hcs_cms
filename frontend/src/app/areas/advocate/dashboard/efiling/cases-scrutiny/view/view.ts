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
  filingsUnderScrutiny: any[] | null = null;

  constructor(private eFilingService: EfilingService) {}

  ngOnInit() {
    this.get_filings_under_scrutiny();
  }

  get_filings_under_scrutiny() {
    this.eFilingService.get_filings_under_scrutiny().subscribe({
      next: (data) => {
        this.filingsUnderScrutiny = data.results;
        console.log(this.filingsUnderScrutiny);
      },
    });
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
    if (normalizedStatus.includes('reject') || normalizedStatus.includes('object')) {
      return 'Rejected';
    }
    return status ?? 'Under Scrutiny';
  }

  getStatusBadgeClass(status: string | null): string {
    const label = this.getStatusLabel(status).toLowerCase();
    if (label.includes('accept')) {
      return 'background: #f1f5f9; color: #1e293b';
    }
    if (label.includes('reject') || label.includes('partial')) {
      return 'background: #fee2e2; color: #991b1b';
    }
    return 'background: #fef3c7; color: #92400e';
  }
}
