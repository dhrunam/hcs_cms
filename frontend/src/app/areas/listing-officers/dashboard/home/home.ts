import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin, catchError, of } from 'rxjs';
import Swal from 'sweetalert2';

import { CauseListService, DraftPreviewItem } from '../../../../services/listing/cause-list.service';
import { benchLabel, BENCH_LABELS, BenchKey } from '../../shared/bench-labels';
import { app_url } from '../../../../environment';

type BenchState = {
  bench_key: string;
  cause_list_id: number | null;
  items: DraftPreviewItem[];
  forwardItems: DraftPreviewItem[];
  pdfUrl: string | null;
  isSaving: boolean;
  isPublishing: boolean;
  isForwarding: boolean;
};

@Component({
  selector: 'app-listing-home',
  imports: [CommonModule, FormsModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class ListingOfficerHome {
  selectedDate: string = new Date().toISOString().slice(0, 10);
  isLoading = false;

  readonly benchKeys: BenchKey[] = Object.keys(BENCH_LABELS) as BenchKey[];
  benchLabel = benchLabel;

  benchStates: BenchState[] = this.benchKeys.map((b) => ({
    bench_key: b,
    cause_list_id: null,
    items: [],
    forwardItems: [],
    pdfUrl: null,
    isSaving: false,
    isPublishing: false,
    isForwarding: false,
  }));

  constructor(private causeListService: CauseListService) {}

  publishError: string | null = null;

  ngOnInit(): void {
    this.loadAllPreviews();
  }

  onDateChange(): void {
    this.loadAllPreviews();
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

    const forwardRequests = this.benchStates.map((state) =>
      this.causeListService.getDraftPreview(this.selectedDate, state.bench_key, false).pipe(
        catchError((err) => {
          console.warn('Failed to load forward items', state.bench_key, err);
          return of({ cause_list_id: null, items: [], bench_key: state.bench_key, cause_list_date: this.selectedDate });
        }),
      ),
    );

    forkJoin([forkJoin(approvedRequests), forkJoin(forwardRequests)]).subscribe(
      ([approvedResps, forwardResps]) => {
        approvedResps.forEach((resp: any, i: number) => {
          const s = this.benchStates[i];
          s.cause_list_id = resp.cause_list_id;
          s.items = resp.items ?? [];
          s.pdfUrl = null; // will be filled from published lists call
          s.isSaving = false;
          s.isPublishing = false;
        });

        forwardResps.forEach((resp: any, i: number) => {
          const s = this.benchStates[i];
          s.forwardItems = (resp.items ?? []).map((item: DraftPreviewItem) => ({
            ...item,
            included: false,
          }));
        });

        // Load published PDFs for the date so View PDF works reliably.
        this.causeListService.getPublishedCauseLists(this.selectedDate).subscribe({
          next: (pub) => {
            const map = new Map<string, string | null>();
            (pub?.items ?? []).forEach((i: any) => map.set(i.bench_key, i.pdf_url ?? null));
            this.benchStates = this.benchStates.map((s) => ({
              ...s,
              pdfUrl: map.get(s.bench_key) ?? s.pdfUrl,
            }));
            this.isLoading = false;
          },
          error: () => {
            this.isLoading = false;
          },
        });
      },
    );
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

  forwardToJudges(state: BenchState): void {
    if (!this.selectedDate) return;
    const ids = (state.forwardItems || [])
      .filter((i) => i.included === true)
      .map((i) => i.efiling_id);
    if (!ids.length) return;

    state.isForwarding = true;
    const payload = {
      forwarded_for_date: this.selectedDate,
      bench_key: state.bench_key,
      efiling_ids: ids,
    };

    this.causeListService.forwardToCourtroom(payload).subscribe({
      next: (resp: any) => {
        state.isForwarding = false;
        const updated = Number(resp?.updated ?? 0);
        const skipped = Number(resp?.skipped ?? 0);
        Swal.fire({
          title: 'Forwarded',
          text: `Forwarded ${updated} case(s) to judges${skipped > 0 ? `, skipped ${skipped}` : ''}.`,
          icon: skipped > 0 ? 'warning' : 'success',
          timer: 1400,
          showConfirmButton: false,
        });
      },
      error: (err) => {
        console.warn('forward failed', err);
        state.isForwarding = false;
        Swal.fire({
          title: 'Forward Failed',
          text: err?.error?.detail || 'Failed to forward cases.',
          icon: 'error',
        });
      },
    });
  }

  selectedForwardCount(state: BenchState): number {
    return (state.forwardItems || []).filter((i) => i.included === true).length;
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

