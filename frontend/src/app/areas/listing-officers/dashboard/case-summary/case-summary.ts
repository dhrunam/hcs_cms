import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { FormsModule } from '@angular/forms';

import { EfilingService } from '../../../../services/advocate/efiling/efiling.services';
import { CauseListService } from '../../../../services/listing/cause-list.service';
import { benchLabel, BENCH_LABELS, BenchKey } from '../../shared/bench-labels';

type Filing = any;
type CaseDetails = any;
type Litigant = any;

@Component({
  selector: 'app-listing-case-summary',
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './case-summary.html',
  styleUrl: './case-summary.css',
})
export class ListingCaseSummaryPage {
  isLoading = false;
  isSaving = false;
  loadError = '';

  filingId: number | null = null;

  filing: Filing | null = null;
  caseDetails: CaseDetails | null = null;
  litigants: Litigant[] = [];

  benchKeys: BenchKey[] = Object.keys(BENCH_LABELS) as BenchKey[];
  benchLabel = benchLabel;
  selectedBench: BenchKey | null = null;

  constructor(
    private route: ActivatedRoute,
    private efilingService: EfilingService,
    private causeListService: CauseListService,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.filingId = Number.isFinite(id) ? id : null;
    if (!this.filingId) {
      this.loadError = 'Missing filing id.';
      return;
    }
    this.load();
  }

  private load(): void {
    if (!this.filingId) return;
    this.isLoading = true;
    this.loadError = '';

    forkJoin({
      filing: this.efilingService.get_filing_by_id(this.filingId),
      caseDetails: this.efilingService.get_case_details_by_filing_id(this.filingId),
      litigants: this.efilingService.get_litigant_list_by_filing_id(this.filingId),
    }).subscribe({
      next: ({ filing, caseDetails, litigants }) => {
        this.filing = filing;
        this.caseDetails = Array.isArray(caseDetails?.results)
          ? caseDetails.results[0] ?? null
          : Array.isArray(caseDetails)
            ? caseDetails[0] ?? null
            : null;
        this.litigants = Array.isArray(litigants?.results) ? litigants.results : Array.isArray(litigants) ? litigants : [];

        const existingBench = (this.filing?.bench as string | null) ?? null;
        this.selectedBench = (this.benchKeys.includes(existingBench as BenchKey) ? (existingBench as BenchKey) : this.benchKeys[0]) ?? null;

        this.isLoading = false;
      },
      error: (err) => {
        console.warn('Failed to load case summary', err);
        this.loadError = 'Failed to load case summary.';
        this.isLoading = false;
      },
    });
  }

  get petitionerName(): string {
    const pet = this.litigants.find((l: any) => l?.is_petitioner === true);
    return pet?.name || this.filing?.petitioner_name || '-';
  }

  get respondentName(): string {
    const res = this.litigants.find((l: any) => l?.is_petitioner === false);
    return res?.name || '-';
  }

  get isBenchLocked(): boolean {
    return !!this.filing?.bench && String(this.filing?.bench).trim().length > 0;
  }

  saveBench(): void {
    if (!this.filingId || !this.selectedBench || this.isBenchLocked) return;
    this.isSaving = true;
    this.causeListService
      .assignBenches([{ efiling_id: this.filingId, bench_key: this.selectedBench }])
      .subscribe({
        next: () => {
          if (this.filing) this.filing.bench = this.selectedBench;
          this.isSaving = false;
        },
        error: (err) => {
          console.warn('Failed to assign bench', err);
          this.isSaving = false;
        },
      });
  }
}

