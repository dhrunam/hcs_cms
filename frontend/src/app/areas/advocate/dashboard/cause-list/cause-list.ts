import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { CauseListService } from '../../../../services/listing/cause-list.service';

type LookupResponse = {
  found: boolean;
  bench_key?: string;
  serial_no?: number | null;
  pdf_url?: string | null;
};

@Component({
  selector: 'app-advocate-cause-list',
  imports: [CommonModule, FormsModule],
  templateUrl: './cause-list.html',
  styleUrl: './cause-list.css',
})
export class CauseListPage {
  selectedDate: string = new Date().toISOString().slice(0, 10);
  caseNumber: string = '';
  isSearching = false;
  result: LookupResponse | null = null;
  errorMessage = '';

  constructor(private causeListService: CauseListService) {}

  search(): void {
    this.errorMessage = '';
    this.result = null;

    if (!this.selectedDate || !this.caseNumber.trim()) {
      this.errorMessage = 'Please enter both cause list date and case number.';
      return;
    }

    this.isSearching = true;
    this.causeListService
      .lookupEntryByCaseNumber(this.selectedDate, this.caseNumber.trim())
      .subscribe({
        next: (resp) => {
          this.result = resp as LookupResponse;
          this.isSearching = false;
        },
        error: (err) => {
          console.warn('Cause list lookup failed', err);
          this.isSearching = false;
          this.errorMessage = 'Failed to search cause list. Please try again.';
        },
      });
  }
}

