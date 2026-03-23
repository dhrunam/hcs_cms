import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

interface PendingCase {
  id: number;
  caseTitle: string;
  filingType: string;
  filedOn: string;
  status: string;
}

@Component({
  selector: 'app-pending-cases',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pending-cases.html',
  styleUrls: ['./pending-cases.css'],
})
export class PendingCases {
  cases: PendingCase[] = [];

  get hasCases(): boolean {
    return this.cases.length > 0;
  }

  getStatusLabel(status: string | null): string {
    const s = (status ?? '').trim().toLowerCase();
    if (!s || s.includes('pending') || s.includes('scrutiny')) return 'Under Scrutiny';
    if (s.includes('accept')) return 'Accepted';
    if (s.includes('reject') || s.includes('partial')) return s.includes('partial') ? 'Partially Rejected' : 'Rejected';
    return status ?? 'Under Scrutiny';
  }

  getStatusBadgeClass(status: string | null): string {
    const label = this.getStatusLabel(status).toLowerCase();
    if (label.includes('accept')) return 'status-badge-success';
    if (label.includes('reject') || label.includes('partial')) return 'status-badge-danger';
    return 'status-badge-warning';
  }
}

