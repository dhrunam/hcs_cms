import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { catchError, of } from 'rxjs';

import { CauseListService } from '../../../../services/listing/cause-list.service';
import { benchLabel, BENCH_LABELS, BenchKey } from '../../shared/bench-labels';

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
          assigned_bench: c.bench ? c.bench : this.benchKeys[0],
        }));
        this.isLoading = false;
      });
  }

  private hasBench(c: RegisteredCase): boolean {
    return !!c.bench && String(c.bench).trim().length > 0;
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

  saveAssignments(): void {
    this.isSaving = true;

    const unassigned = this.unassignedCases;
    if (unassigned.length === 0) {
      this.isSaving = false;
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

