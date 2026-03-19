import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { EfilingService } from '../../../../../services/advocate/efiling/efiling.services';

interface EfilingCaseType {
  type_name?: string;
}

interface EfilingItem {
  id: number;
  petitioner_name: string;
  petitioner_contact: string;
  e_filing_number: string;
  created_at: string;
  status: string | null;
  case_type: EfilingCaseType | null;
}

@Component({
  selector: 'app-filed-cases-view',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class FiledCasesView {
  filedCases: EfilingItem[] = [];
  isLoading = false;

  constructor(private eFilingService: EfilingService) {}

  ngOnInit(): void {
    this.getFiledCases();
  }

  getFiledCases(): void {
    this.isLoading = true;
    this.eFilingService.get_filings_under_scrutiny().subscribe({
      next: (data) => {
        this.filedCases = data?.results ?? [];
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load filed cases', error);
        this.filedCases = [];
        this.isLoading = false;
      },
    });
  }

  getStatusLabel(status: string | null): string {
    const normalizedStatus = (status ?? '').trim().toLowerCase();

    if (!normalizedStatus || normalizedStatus === 'submitted') {
      return 'Under Scrutiny';
    }

    if (normalizedStatus.includes('accept')) {
      return 'Accepted';
    }

    if (
      normalizedStatus.includes('reject') ||
      normalizedStatus.includes('object') ||
      normalizedStatus.includes('defect')
    ) {
      return 'Objection';
    }

    return status ?? 'Under Scrutiny';
  }
}
