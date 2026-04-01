import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin, catchError, of } from 'rxjs';

import {
  BenchConfiguration,
  CauseListService,
  DraftPreviewItem,
} from '../../../../services/listing/cause-list.service';
import { app_url } from '../../../../environment';

type BenchState = {
  bench_key: string;
  cause_list_id: number | null;
  items: DraftPreviewItem[];
  pdfUrl: string | null;
  isSaving: boolean;
  isPublishing: boolean;
};

@Component({
  selector: 'app-listing-home',
  imports: [CommonModule, FormsModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class ListingOfficerHome {
  selectedDate: string = new Date().toISOString().slice(0, 10);
  selectedMonth: string = new Date().toISOString().slice(0, 7);
  isLoading = false;
  isCalendarLoading = false;
  monthDays: Array<{ date: string; day: number; publishedCount: number; hasAny: boolean }> = [];
  publishedBenchSummary: Array<{ bench_key: string; included_count: number; pdf_url: string | null }> = [];
  benchConfigurations: BenchConfiguration[] = [];
  benchStates: BenchState[] = [];

  constructor(private causeListService: CauseListService) {}

  publishError: string | null = null;

  ngOnInit(): void {
    this.causeListService.getBenchConfigurations().subscribe({
      next: (resp) => {
        this.benchConfigurations = resp?.items ?? [];
        this.benchStates = this.benchConfigurations.map((bench) => ({
          bench_key: bench.bench_key,
          cause_list_id: null,
          items: [],
          pdfUrl: null,
          isSaving: false,
          isPublishing: false,
        }));
        this.loadAllPreviews();
        this.loadMonthCalendar();
      },
      error: (err) => {
        console.warn('Failed to load bench configurations', err);
        this.benchConfigurations = [];
        this.benchStates = [];
        this.loadAllPreviews();
        this.loadMonthCalendar();
      },
    });
  }

  onDateChange(): void {
    this.loadAllPreviews();
  }

  onMonthChange(): void {
    this.loadMonthCalendar();
  }

  private loadAllPreviews(): void {
    if (!this.selectedDate) return;

    this.isLoading = true;

    const approvedRequests = this.benchStates.map((state) =>
      this.causeListService.getDraftPreview(this.selectedDate, state.bench_key, true).pipe(
        catchError((err) => {
          console.warn('Failed to load approved draft preview', state.bench_key, err);
          return of({ cause_list_id: null, items: [], bench_key: state.bench_key, cause_list_date: this.selectedDate });
        }),
      ),
    );

    forkJoin(approvedRequests).subscribe(
      (approvedResps) => {
        approvedResps.forEach((resp: any, i: number) => {
          const s = this.benchStates[i];
          s.cause_list_id = resp.cause_list_id;
          s.items = resp.items ?? [];
          s.pdfUrl = null; // will be filled from published lists call
          s.isSaving = false;
          s.isPublishing = false;
        });

        // Load published PDFs for the date so View PDF works reliably.
        this.causeListService.getPublishedCauseLists(this.selectedDate).subscribe({
          next: (pub) => {
            const map = new Map<string, string | null>();
            (pub?.items ?? []).forEach((i: any) => map.set(i.bench_key, i.pdf_url ?? null));
            this.publishedBenchSummary = (pub?.items ?? []).map((i: any) => ({
              bench_key: String(i?.bench_key || ''),
              included_count: Number(i?.included_count ?? 0),
              pdf_url: i?.pdf_url ?? null,
            }));
            this.benchStates = this.benchStates.map((s) => ({
              ...s,
              pdfUrl: map.get(s.bench_key) ?? s.pdfUrl,
            }));
            this.isLoading = false;
          },
          error: () => {
            this.publishedBenchSummary = [];
            this.isLoading = false;
          },
        });
      },
    );
  }

  private loadMonthCalendar(): void {
    const month = this.selectedMonth;
    if (!month || !/^\d{4}-\d{2}$/.test(month)) return;
    const [y, m] = month.split('-').map((x) => Number(x));
    const daysInMonth = new Date(y, m, 0).getDate();
    const dates = Array.from({ length: daysInMonth }, (_, i) => {
      const day = i + 1;
      return `${month}-${String(day).padStart(2, '0')}`;
    });
    this.isCalendarLoading = true;
    const requests = dates.map((d) =>
      this.causeListService.getPublishedCauseLists(d).pipe(
        catchError(() => of({ items: [] })),
      ),
    );
    forkJoin(requests).subscribe({
      next: (rows) => {
        this.monthDays = rows.map((r: any, idx: number) => {
          const date = dates[idx];
          const publishedCount = (r?.items ?? []).length;
          return {
            date,
            day: Number(date.slice(-2)),
            publishedCount,
            hasAny: publishedCount > 0,
          };
        });
        this.isCalendarLoading = false;
      },
      error: () => {
        this.monthDays = [];
        this.isCalendarLoading = false;
      },
    });
  }

  openDateFromCalendar(date: string): void {
    this.selectedDate = date;
    this.loadAllPreviews();
  }

  benchLabel(key: string | null | undefined): string {
    if (!key) return '-';
    const normalizedKey = String(key).trim();
    return this.benchConfigurations.find((item) => item.bench_key === normalizedKey)?.label || normalizedKey;
  }

  get publishedMonthDays(): Array<{ date: string; day: number; publishedCount: number; hasAny: boolean }> {
    return this.monthDays.filter((d) => d.hasAny);
  }

  saveDraft(state: BenchState): void {
    if (!this.selectedDate) return;

    state.isSaving = true;
    const payload = {
      cause_list_date: this.selectedDate,
      bench_key: state.bench_key,
      entries: state.items.map((i) => ({
        efiling_id: i.efiling_id,
        serial_no: i.serial_no,
        included: i.included,
      })),
    };

    this.causeListService.saveDraft(payload).subscribe({
      next: (resp) => {
        state.cause_list_id = resp.cause_list_id;
        state.isSaving = false;
      },
      error: (err) => {
        console.warn('saveDraft failed', err);
        state.isSaving = false;
      },
    });
  }

  includedCount(state: BenchState): number {
    return (state.items || []).filter((i) => i.included).length;
  }

  draftPdfUrl(state: BenchState): string | null {
    if (!this.selectedDate) return null;
    return this.causeListService.getDraftPdfUrl(this.selectedDate, state.bench_key);
  }

  publish(state: BenchState): void {
    this.publishError = null;
    state.isPublishing = true;
    const payload = {
      cause_list_date: this.selectedDate,
      bench_key: state.bench_key,
      entries: (state.items || []).map((i) => ({
        efiling_id: i.efiling_id,
        serial_no: i.serial_no,
        included: i.included,
      })),
    };

    this.causeListService.publishCauseListDirect(payload).subscribe({
      next: (resp) => {
        // Backend should return absolute. If not, fallback to app_url.
        const url = resp.pdf_url;
        state.pdfUrl = url && url.startsWith('/media/') ? `${app_url}${url}` : url;
        state.isPublishing = false;
        // refresh published list badges/links
        this.loadAllPreviews();
      },
      error: (err) => {
        console.warn('publish failed', err);
        this.publishError = err?.error?.detail || 'Publish failed.';
        state.isPublishing = false;
      },
    });
  }
}

