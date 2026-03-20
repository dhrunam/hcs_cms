import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-view',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class View implements OnInit {
  documents: any[] = [];
  isLoading = true;

  constructor(private eFilingService: EfilingService) {}

  ngOnInit(): void {
    this.eFilingService.get_efiling_documents().subscribe({
      next: (res) => {
        const rows = Array.isArray(res) ? res : Array.isArray(res?.results) ? res.results : [];
        this.documents = rows;
        this.isLoading = false;
      },
      error: () => {
        this.documents = [];
        this.isLoading = false;
      },
    });
  }

  trackByDocId(_: number, item: any): number {
    return item?.id;
  }
}

