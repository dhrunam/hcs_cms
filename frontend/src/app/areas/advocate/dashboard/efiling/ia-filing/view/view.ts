import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-ia-filing-view',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class IaFilingView implements OnInit {
  iaFilings: any[] = [];
  isLoading = true;

  constructor(private efilingService: EfilingService) {}

  ngOnInit(): void {
    this.efilingService.get_ias().subscribe({
      next: (res) => {
        this.iaFilings = Array.isArray(res) ? res : res?.results ?? [];
        this.isLoading = false;
      },
      error: () => {
        this.iaFilings = [];
        this.isLoading = false;
      },
    });
  }

  trackById(_: number, item: any): number {
    return item?.id ?? 0;
  }

  getStatusLabel(status: string | null): string {
    const s = (status ?? '').trim().toLowerCase();
    if (!s || s.includes('pending') || s.includes('scrutiny') || s.includes('submitted')) return s.includes('scrutiny') ? 'Under Scrutiny' : (status || 'Pending');
    if (s.includes('accept')) return 'Accepted';
    if (s.includes('reject') || s.includes('partial')) return s.includes('partial') ? 'Partially Rejected' : 'Rejected';
    return status ?? 'Pending';
  }

  getStatusBadgeClass(status: string | null): string {
    const label = this.getStatusLabel(status).toLowerCase();
    if (label.includes('accept')) return 'status-badge-success';
    if (label.includes('reject') || label.includes('partial')) return 'status-badge-danger';
    return 'status-badge-warning';
  }
}
