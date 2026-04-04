import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { CourtroomService } from '../../../../services/judge/courtroom.service';

@Component({
  selector: 'app-advocate-cause-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './cause-list.html',
  styleUrl: './cause-list.css',
})
export class CauseListPage implements OnInit {
  selectedDate: string = new Date().toISOString().slice(0, 10);
  isLoading = false;
  todaysCases: any[] = [];
  errorMessage = '';

  constructor(private courtroomService: CourtroomService) {}

  ngOnInit(): void {
    this.refreshHearings();
  }

  refreshHearings(): void {
    this.errorMessage = '';
    this.isLoading = true;
    this.todaysCases = [];

    this.courtroomService
      .getPendingCases(this.selectedDate)
      .subscribe({
        next: (resp) => {
          // Unified API returns cases in 'pending_for_causelist' once published
          this.todaysCases = resp?.pending_for_causelist ?? [];
          this.isLoading = false;
          if (this.todaysCases.length === 0) {
            this.errorMessage = 'No published hearings found for you on this date.';
          }
        },
        error: (err) => {
          console.warn('Failed to load advocate hearings', err);
          this.isLoading = false;
          this.errorMessage = 'Unable to retrieve scheduled hearings at this moment.';
        },
      });
  }

  onDateChange(): void {
    this.refreshHearings();
  }
}

