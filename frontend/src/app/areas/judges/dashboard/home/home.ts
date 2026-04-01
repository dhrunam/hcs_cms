import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { CourtroomService } from '../../../../services/judge/courtroom.service';
import { benchLabel } from '../../../listing-officers/shared/bench-labels';

@Component({
  selector: 'app-judge-pending-cases',
  imports: [CommonModule, FormsModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class JudgePendingCasesPage {
  benchLabel = benchLabel;
  forwardedForDate: string = new Date().toISOString().slice(0, 10);
  isLoading = false;
  loadError = '';

  pendingForListing: {
    efiling_id: number;
    e_filing_number?: string | null;
    case_number: string | null;
    petitioner_name?: string | null;
    petitioner_vs_respondent?: string | null;
    bench_key: string;
    bench_label?: string;
    judge_decision: boolean | null;
    forwarded_for_date?: string;
  }[] = [];
  pendingForCauseList: {
    efiling_id: number;
    e_filing_number?: string | null;
    case_number: string | null;
    petitioner_name?: string | null;
    petitioner_vs_respondent?: string | null;
    bench_key: string;
    bench_label?: string;
    judge_decision: boolean | null;
    forwarded_for_date?: string;
  }[] = [];
  calendarItems: {
    efiling_id: number;
    e_filing_number?: string | null;
    case_number: string | null;
    petitioner_name?: string | null;
    petitioner_vs_respondent?: string | null;
    status: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS';
    decision_notes: string | null;
  }[] = [];

  constructor(private courtroomService: CourtroomService, private router: Router) {}

  ngOnInit(): void {
    this.load();
  }

  onDateChange(): void {
    this.load();
  }

  private load(): void {
    this.isLoading = true;
    this.loadError = '';

    this.courtroomService.getPendingCases(this.forwardedForDate).subscribe({
      next: (resp) => {
        this.pendingForListing = resp?.pending_for_listing ?? [];
        this.pendingForCauseList = resp?.pending_for_causelist ?? [];
        this.loadCalendar();
        this.isLoading = false;
      },
      error: (err) => {
        console.warn('Failed to load judge pending cases', err);
        this.loadError = 'Failed to load pending cases.';
        this.isLoading = false;
      },
    });
  }

  openCourtroom(efilingId: number): void {
    const c =
      this.pendingForListing.find((x) => x.efiling_id === efilingId) ||
      this.pendingForCauseList.find((x) => x.efiling_id === efilingId);
    const fdate = c?.forwarded_for_date || this.forwardedForDate;
    this.router.navigate(['/judges/dashboard/courtroom', efilingId], {
      queryParams: { forwarded_for_date: fdate },
    });
  }

  private loadCalendar(): void {
    this.courtroomService.getDecisionCalendar().subscribe({
      next: (resp) => {
        this.calendarItems = resp?.items ?? [];
      },
      error: (err) => {
        console.warn('Failed to load decision calendar', err);
        this.calendarItems = [];
      },
    });
  }

  statusBadge(status: string): string {
    if (status === 'APPROVED') return 'text-bg-success';
    if (status === 'DECLINED') return 'text-bg-danger';
    return 'text-bg-warning';
  }
}

