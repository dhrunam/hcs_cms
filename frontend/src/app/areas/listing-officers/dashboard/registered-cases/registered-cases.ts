import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { catchError, of } from 'rxjs';
import Swal from 'sweetalert2';

import { CauseListService } from '../../../../services/listing/cause-list.service';
import { benchLabel, isUnassignedBench } from '../../shared/bench-labels';

type RegisteredCase = {
  efiling_id: number;
  case_number: string | null;
  petitioner_name: string | null;
  respondent_name: string | null;
  petitioner_vs_respondent?: string | null;
  bench: string | null;

  cause_of_action: string | null;
  date_of_cause_of_action: string | null;
  dispute_state: string | null;
  dispute_district: string | null;
  dispute_taluka: string | null;
  approval_status?: 'NOT_FORWARDED' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'REQUESTED_DOCS';
  approval_notes?: string[];
  approval_bench_key?: string | null;
  approval_forwarded_for_date?: string | null;
  approval_listing_date?: string | null;
  listing_summary?: string | null;
  requested_documents?: { document_index_id: number; document_part_name: string | null; document_type: string | null }[];
};

@Component({
  selector: 'app-registered-cases',
  imports: [CommonModule, FormsModule],
  templateUrl: './registered-cases.html',
  styleUrl: './registered-cases.css',
})
export class RegisteredCasesPage {
  isLoading = false;

  cases: RegisteredCase[] = [];
  benchLabel = benchLabel;

  loadError = '';

  constructor(private causeListService: CauseListService, private router: Router) {}

  ngOnInit(): void {
    this.loadRegisteredCases();
  }

  private loadRegisteredCases(): void {
    this.loadError = '';
    this.isLoading = true;

    this.causeListService
      .getRegisteredCases({ page_size: 200 })
      .pipe(
        catchError((err) => {
          console.warn('Failed to load registered cases', err);
          this.isLoading = false;
          this.loadError = 'Failed to load registered cases.';
          return of({ items: [] });
        }),
      )
      .subscribe((resp) => {
        this.cases = (resp?.items ?? []).map((c: any) => ({ ...c }));
        this.isLoading = false;
      });
  }

  private hasBench(c: RegisteredCase): boolean {
    return !isUnassignedBench(c.bench);
  }

  get unassignedCases(): RegisteredCase[] {
    return (this.cases ?? []).filter((c) => !this.hasBench(c));
  }

  get listedCases(): RegisteredCase[] {
    return (this.cases ?? []).filter((c) => this.hasBench(c));
  }

  get canProceedToGenerator(): boolean {
    return this.cases.length > 0;
  }

  approvalStatusLabel(c: RegisteredCase): string {
    switch (c.approval_status) {
      case 'APPROVED':
        return 'Approved';
      case 'REJECTED':
        return 'Rejected';
      case 'REQUESTED_DOCS':
        return 'Approval Pending';
      case 'PENDING':
        return 'Forwarded (Approval Pending)';
      default:
        return 'Not Forwarded';
    }
  }

  approvalBadgeClass(c: RegisteredCase): string {
    switch (c.approval_status) {
      case 'APPROVED':
        return 'text-bg-success';
      case 'REJECTED':
        return 'text-bg-danger';
      case 'REQUESTED_DOCS':
        return 'text-bg-warning';
      case 'PENDING':
        return 'text-bg-warning';
      default:
        return 'text-bg-secondary';
    }
  }

  proceedToGenerator(): void {
    const assignedCount = this.listedCases.length;
    if (assignedCount === 0) {
      Swal.fire({
        title: 'No Assigned Cases',
        text: 'Open a case, select bench for forwarding, and forward to judges first.',
        icon: 'warning',
      });
      return;
    }
    this.router.navigate(['/listing-officers/dashboard/generate-cause-list']);
  }

  openCase(efilingId: number): void {
    this.router.navigate(['/listing-officers/dashboard/case', efilingId]);
  }
}

