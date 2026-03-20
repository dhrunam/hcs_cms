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

  constructor(private efilingService: EfilingService) {}

  ngOnInit(): void {
    this.loadFilingCounts();
  }

  loadFilingCounts(): void {
    this.isLoading = true;
    forkJoin({
      draft: this.efilingService.get_filings_under_draft(),
      scrutiny: this.efilingService.get_filings_under_scrutiny(),
    }).subscribe({
      next: ({ draft, scrutiny }) => {
        const draftRows = draft?.results ?? [];
        const scrutinyRows = scrutiny?.results ?? [];
        const all = [...draftRows, ...scrutinyRows];

        const statusLower = (s: string) => (s ?? '').trim().toLowerCase();

        this.totalFilings = all.length;
        this.pendingFilings = all.filter((f: any) => {
          const s = statusLower(f?.status);
          return s === 'under_scrutiny' || s.includes('scrutiny') || s.includes('pending') || s === 'draft';
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
