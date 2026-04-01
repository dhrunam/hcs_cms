import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, of } from 'rxjs';
import Swal from 'sweetalert2';

import {
  BenchConfiguration,
  CauseListService,
} from '../../../../services/listing/cause-list.service';

type ListedCase = {
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
};

@Component({
  selector: 'app-listed-cases',
  imports: [CommonModule],
  templateUrl: './listed-cases.html',
  styleUrl: './listed-cases.css',
})
export class ListedCasesPage {
  isLoading = false;
  cases: ListedCase[] = [];
  loadError = '';
  benchConfigurations: BenchConfiguration[] = [];

  constructor(private causeListService: CauseListService, private router: Router) {}

  ngOnInit(): void {
    this.loadBenchConfigurations();
    this.loadListedCases();
  }

  private loadBenchConfigurations(): void {
    this.causeListService.getBenchConfigurations().subscribe({
      next: (resp) => {
        this.benchConfigurations = resp?.items ?? [];
      },
      error: (err) => {
        console.warn('Failed to load bench configurations', err);
        this.benchConfigurations = [];
      },
    });
  }

  private loadListedCases(): void {
    this.loadError = '';
    this.isLoading = true;

    this.causeListService
      .getRegisteredCases({ page_size: 200 })
      .pipe(
        catchError((err) => {
          console.warn('Failed to load listed cases', err);
          this.isLoading = false;
          this.loadError = 'Failed to load listed cases.';
          return of({ items: [] });
        }),
      )
      .subscribe((resp) => {
        this.cases = (resp?.items ?? []).filter((c: ListedCase) => !this.isUnassignedBench(c.bench));
        this.isLoading = false;
      });
  }

  benchLabel(key: string | null | undefined): string {
    if (this.isUnassignedBench(key)) return '-';
    const normalizedKey = String(key ?? '').trim();
    return this.benchConfigurations.find((item) => item.bench_key === normalizedKey)?.label || normalizedKey;
  }

  private isUnassignedBench(key: string | null | undefined): boolean {
    const value = String(key ?? '').trim().toLowerCase();
    return !value || value === 'high court of sikkim' || value === 'high court of skkim';
  }

  get canProceedToGenerator(): boolean {
    return this.cases.length > 0;
  }

  proceedToGenerator(): void {
    if (this.cases.length === 0) {
      Swal.fire({
        title: 'No Listed Cases',
        text: 'Assign at least one bench before generating the cause list.',
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