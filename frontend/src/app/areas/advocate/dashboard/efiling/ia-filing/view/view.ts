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
}
