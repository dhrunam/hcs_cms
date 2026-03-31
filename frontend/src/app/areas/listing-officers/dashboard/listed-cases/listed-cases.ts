import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, of } from 'rxjs';
import Swal from 'sweetalert2';

import { CauseListService } from '../../../../services/listing/cause-list.service';
import { benchLabel, isUnassignedBench } from '../../shared/bench-labels';

type ListedCase = {
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
  benchLabel = benchLabel;

  constructor(private causeListService: CauseListService, private router: Router) {}

  ngOnInit(): void {
    this.loadListedCases();
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
        this.cases = (resp?.items ?? []).filter((c: ListedCase) => !isUnassignedBench(c.bench));
        this.isLoading = false;
      });
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