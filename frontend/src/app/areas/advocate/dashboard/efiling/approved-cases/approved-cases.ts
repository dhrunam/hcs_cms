import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { EfilingService } from '../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-approved-cases',
  imports: [CommonModule, RouterLink],
  templateUrl: './approved-cases.html',
  styleUrl: './approved-cases.css',
})
export class ApprovedCases {
  approvedCases: any[] | null = null;

  get hasCases(): boolean {
    return Array.isArray(this.approvedCases) && this.approvedCases.length > 0;
  }

  constructor(private eFilingService: EfilingService) {}

  ngOnInit() {
    this.get_approved_cases();
  }

  get_approved_cases() {
    this.eFilingService.get_approved_cases().subscribe({
      next: (data) => {
        this.approvedCases = data?.results ?? [];
        console.log(this.approvedCases);
      },
    });
  }

  getStatusLabel(status: string | null): string {
    const normalizedStatus = (status ?? '').trim().toLowerCase();
    if (
      !normalizedStatus ||
      normalizedStatus === 'submitted' ||
      normalizedStatus === 'under_scrutiny'
    ) {
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
      return 'status-badge-success';
    }
    if (label.includes('reject') || label.includes('partial')) {
      return 'status-badge-danger';
    }
    return 'status-badge-warning';
  }
}
