import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';
import { EfilingService } from '../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home implements OnInit {
  totalFilings = 0;
  pendingFilings = 0;
  approvedFilings = 0;
  objections = 0;
  advocateName = 'Sagar Pradhan';
  isLoading = true;
  notifications: any[] = [];
  isLoadingNotifications = false;

  constructor(private efilingService: EfilingService) {}

  ngOnInit(): void {
    this.loadFilingCounts();
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.isLoadingNotifications = true;
    this.efilingService.get_notifications('advocate').subscribe({
      next: (data: any) => {
        this.notifications = Array.isArray(data) ? data : (data?.results ?? []);
        this.isLoadingNotifications = false;
      },
      error: () => {
        this.notifications = [];
        this.isLoadingNotifications = false;
      },
    });
  }

  formatNotificationDate(dateStr: string | null): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  }

  private extractResults(payload: any): any[] {
    if (Array.isArray(payload)) return payload;
    if (payload && Array.isArray(payload.results)) return payload.results;
    return [];
  }

  loadFilingCounts(): void {
    this.isLoading = true;
    const pageSize = 9999; // fetch all for accurate dashboard counts
    forkJoin({
      draft: this.efilingService.get_filings_under_draft({ page_size: pageSize }),
      scrutiny: this.efilingService.get_filings_under_scrutiny({ page_size: pageSize }),
      approved: this.efilingService.get_approved_cases({ page_size: pageSize }),
    }).subscribe({
      next: ({ draft, scrutiny, approved }) => {
        const draftRows = this.extractResults(draft);
        const scrutinyRows = this.extractResults(scrutiny);
        const approvedRows = this.extractResults(approved);
        const all = [...draftRows, ...scrutinyRows, ...approvedRows];

        const statusLower = (s: string) => (s ?? '').trim().toLowerCase();

        this.totalFilings = all.length;
        this.pendingFilings = all.filter((f: any) => {
          const s = statusLower(f?.status);
          return s === 'under_scrutiny' || s.includes('scrutiny') || s.includes('pending') || s === 'draft' || !s;
        }).length;
        this.approvedFilings = all.filter((f: any) =>
          statusLower(f?.status).includes('accept'),
        ).length;
        this.objections = all.filter((f: any) => {
          const s = statusLower(f?.status);
          return s.includes('reject') || s.includes('object');
        }).length;

        this.isLoading = false;
      },
      error: () => {
        this.totalFilings = 0;
        this.pendingFilings = 0;
        this.approvedFilings = 0;
        this.objections = 0;
        this.isLoading = false;
      },
    });
  }
}
