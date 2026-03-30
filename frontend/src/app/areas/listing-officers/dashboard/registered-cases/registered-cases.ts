import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { catchError, of } from 'rxjs';
import Swal from 'sweetalert2';

import { CauseListService } from '../../../../services/listing/cause-list.service';
import { benchLabel, BENCH_LABELS, BenchKey, isUnassignedBench, judgesForBench } from '../../shared/bench-labels';

type RegisteredCase = {
  efiling_id: number;
  case_number: string | null;
  petitioner_name: string | null;
  respondent_name: string | null;
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
  listing_summary?: string | null;
  requested_documents?: { document_index_id: number; document_part_name: string | null; document_type: string | null }[];

  // UI-only field
  assigned_bench: string | null;
};

@Component({
  selector: 'app-registered-cases',
  imports: [CommonModule, FormsModule],
  templateUrl: './registered-cases.html',
  styleUrl: './registered-cases.css',
})
export class RegisteredCasesPage {
  isLoading = false;
  isSaving = false;

  cases: RegisteredCase[] = [];
  benchKeys: BenchKey[] = Object.keys(BENCH_LABELS) as BenchKey[];
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
        this.cases = (resp?.items ?? []).map((c: any) => ({
          ...c,
          assigned_bench: !isUnassignedBench(c.bench) ? c.bench : null,
        }));
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
    return this.cases.length > 0 && this.unassignedCases.length === 0;
  }

  canAssignBench(c: RegisteredCase): boolean {
    return c.approval_status === 'APPROVED';
  }

  approvalStatusLabel(c: RegisteredCase): string {
    switch (c.approval_status) {
      case 'APPROVED':
        return 'Approved';
      case 'REJECTED':
        return 'Rejected';
      case 'REQUESTED_DOCS':
        return 'Judge Requested Documents';
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
        return 'text-bg-info';
      case 'PENDING':
        return 'text-bg-warning';
      default:
        return 'text-bg-secondary';
    }
  }

  judgesForCaseForward(c: RegisteredCase): string[] {
    return judgesForBench(c.assigned_bench);
  }

  forwardCaseForApproval(c: RegisteredCase): void {
    if (!c.assigned_bench) return;
    if (c.approval_status === 'PENDING') return;
    const summary = (c.listing_summary || '').trim();
    if (!summary) {
      Swal.fire({
        title: 'Summary Required',
        text: 'Please write a case summary for judge review before forwarding.',
        icon: 'warning',
      });
      return;
    }
    const today = new Date().toISOString().slice(0, 10);
    this.causeListService
      .forwardToCourtroom({
        forwarded_for_date: today,
        bench_key: c.assigned_bench,
        listing_summary: summary,
        document_index_ids:
          c.approval_status === 'REQUESTED_DOCS'
            ? (c.requested_documents ?? []).map((d) => d.document_index_id)
            : undefined,
        efiling_ids: [c.efiling_id],
      })
      .subscribe({
        next: (resp) => {
          const updated = Number(resp?.updated ?? 0);
          const skipped = Number(resp?.skipped ?? 0);
          const errorLines = Array.isArray(resp?.errors) ? resp.errors.map((e: any) => `#${e?.efiling_id}: ${e?.detail}`) : [];
          Swal.fire({
            title: updated > 0 ? 'Forwarded' : 'Not Forwarded',
            text: updated > 0
              ? `Case forwarded to judges for approval.${skipped > 0 ? ` Skipped: ${skipped}` : ''}`
              : (errorLines[0] || 'No case was forwarded.'),
            icon: updated > 0 ? 'success' : 'warning',
            timer: 1200,
            showConfirmButton: false,
          });
          if (updated > 0) {
            c.approval_status = 'PENDING';
            c.approval_forwarded_for_date = today;
            c.approval_bench_key = c.assigned_bench;
          }
          this.loadRegisteredCases();
        },
        error: (err) => {
          console.warn('forward case failed', err);
          Swal.fire({
            title: 'Forward Failed',
            text: err?.error?.detail || 'Failed to forward case for approval.',
            icon: 'error',
          });
        },
      });
  }

  requestedDocsLabel(c: RegisteredCase): string {
    const docs = c.requested_documents ?? [];
    if (!docs.length) return '';
    return docs
      .map((d) => d.document_part_name || `Document #${d.document_index_id}`)
      .join(', ');
  }

  saveAssignments(): void {
    this.isSaving = true;

    const unassigned = this.unassignedCases;
    if (unassigned.length === 0) {
      this.isSaving = false;
      return;
    }
    const notApproved = unassigned.filter((c) => !this.canAssignBench(c));
    if (notApproved.length > 0) {
      this.isSaving = false;
      Swal.fire({
        title: 'Approval Required',
        text: 'Forward case(s) to judges and wait for approval before assigning bench.',
        icon: 'warning',
      });
      return;
    }
    const noBenchSelected = unassigned.filter((c) => !c.assigned_bench);
    if (noBenchSelected.length > 0) {
      this.isSaving = false;
      Swal.fire({
        title: 'Bench Required',
        text: 'Select a bench for all cases before saving assignments.',
        icon: 'warning',
      });
      return;
    }

    const assignments = unassigned.map((c) => ({
      efiling_id: c.efiling_id,
      bench_key: c.assigned_bench || '',
    }));

    this.causeListService.assignBenches(assignments).subscribe({
      next: () => {
        this.isSaving = false;
        // Keep local UI synced to avoid confusion; move assigned cases into "Listed Cases".
        const assignedIds = new Set(assignments.map((a) => a.efiling_id));
        this.cases = this.cases.map((c) =>
          assignedIds.has(c.efiling_id) ? { ...c, bench: c.assigned_bench } : c,
        );
      },
      error: (err) => {
        console.warn('assignBenches failed', err);
        this.isSaving = false;
      },
    });
  }

  proceedToGenerator(): void {
    this.router.navigate(['/listing-officers/dashboard/generate-cause-list']);
  }

  openCase(efilingId: number): void {
    this.router.navigate(['/listing-officers/dashboard/case', efilingId]);
  }
}

