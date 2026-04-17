import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';

import { PurposeOption, ReaderDailyProceedingCase, ReaderService } from '../../../../services/reader/reader.service';

@Component({
  selector: 'app-reader-daily-proceedings',
  imports: [CommonModule, FormsModule],
  templateUrl: './daily-proceedings.html',
  styleUrl: './daily-proceedings.css',
})
export class ReaderDailyProceedingsPage {
  items: ReaderDailyProceedingCase[] = [];
  purposeOptions: PurposeOption[] = [];
  isLoading = false;
  loadError = '';
  purposesLoadError = '';
  selectedCauseListDate = new Date().toISOString().slice(0, 10);
  saveState: Record<number, boolean> = {};
  formState: Record<number, {
    hearing_date: string;
    next_listing_date: string;
    proceedings_text: string;
    steno_purpose_code: number | null;
    listing_remark: string;
  }> = {};

  constructor(private readerService: ReaderService) {}

  ngOnInit(): void {
    this.loadPurposes();
    this.load();
  }

  loadPurposes(): void {
    this.purposesLoadError = '';
    this.readerService.getPurposes().subscribe({
      next: (purposes) => {
        this.purposeOptions = purposes ?? [];
      },
      error: () => {
        this.purposeOptions = [];
        this.purposesLoadError = 'Failed to load purpose options.';
      },
    });
  }

  load(): void {
    this.isLoading = true;
    this.loadError = '';
    this.readerService.getDailyProceedings({
      page_size: 200,
      cause_list_date: this.selectedCauseListDate,
    }).subscribe({
      next: (resp) => {
        this.items = resp?.items ?? [];
        for (const item of this.items) {
          this.formState[item.efiling_id] = {
            hearing_date: item.last_hearing_date || new Date().toISOString().slice(0, 10),
            next_listing_date: item.last_next_listing_date || new Date().toISOString().slice(0, 10),
            proceedings_text: item.latest_proceedings_text || '',
            steno_purpose_code: item.latest_steno_purpose_code ?? null,
            listing_remark: '',
          };
        }
        this.isLoading = false;
      },
      error: () => {
        this.loadError = 'Failed to load daily proceedings for selected published cause list date.';
        this.isLoading = false;
      },
    });
  }

  submit(item: ReaderDailyProceedingCase): void {
    const state = this.formState[item.efiling_id];
    if (!state) return;
    this.saveState[item.efiling_id] = true;
    this.readerService
      .submitDailyProceeding({
        efiling_id: item.efiling_id,
        hearing_date: state.hearing_date,
        next_listing_date: state.next_listing_date,
        proceedings_text: state.proceedings_text,
        steno_purpose_code: state.steno_purpose_code,
        listing_remark: state.listing_remark,
      })
      .subscribe({
        next: () => {
          this.saveState[item.efiling_id] = false;
          Swal.fire({ title: 'Saved', text: 'Proceedings sent to listing and steno workflow.', icon: 'success', timer: 1200, showConfirmButton: false });
          this.load();
        },
        error: (err) => {
          this.saveState[item.efiling_id] = false;
          const detail = String(err?.error?.detail || '').trim();
          const isMappingIssue =
            detail.includes('No active steno mapping found') ||
            detail.toLowerCase().includes('judge-steno mapping');
          Swal.fire(
            'Error',
            isMappingIssue
              ? 'No active Judge-Steno mapping found for this bench. Please configure mapping, then submit proceedings again.'
              : (detail || 'Failed to submit proceedings'),
            'error',
          );
        },
      });
  }

  purposeLabel(purpose: PurposeOption): string {
    return purpose.purpose_name || purpose.lpurpose_name || `Purpose #${purpose.purpose_code}`;
  }
}
