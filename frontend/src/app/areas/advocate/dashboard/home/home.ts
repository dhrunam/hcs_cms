import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { EfilingService } from '../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-home',
  imports: [CommonModule, RouterModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  totalFilings: number = 0;
  pendingFilings: number = 0;
  approvedFilings: number = 0;
  objections: number = 0;
  advocateName: string = 'Sagar Pradhan';
  filingsUnderScrutiny: any[] = [];

  constructor(private eFilingService: EfilingService) {}

  ngOnInit(): void {
    this.getFilingNumbers();
    this.getFilingsUnderScrutiny();
  }

  ngAfterViewInit(): void {
    const allValues = document.querySelectorAll('.value');
    allValues.forEach((singleValue: any) => {
      let startValue = 0;
      const endValue = parseInt(singleValue.getAttribute('data-value'));
      if (endValue !== 0) {
        const duration = Math.floor(1000 / endValue);
        const counter = setInterval(() => {
          startValue += 1;
          singleValue.textContent = startValue;
          if (startValue === endValue) {
            clearInterval(counter);
          }
        }, duration);
      }
    });
  }

  getFilingNumbers() {
    this.totalFilings = 148;
    this.pendingFilings = 32;
    this.approvedFilings = 96;
    this.objections = 20;
  }

  getFilingsUnderScrutiny() {
    this.eFilingService.get_filings_under_scrutiny().subscribe({
      next: (data: any) => {
        const rows = Array.isArray(data?.results) ? data.results : [];
        this.filingsUnderScrutiny = rows.slice(0, 5);
      },
    });
  }

  getCaseTitle(row: any): string {
    return row?.case_title || row?.case_title_name || row?.caseTitle || row?.title || '-';
  }

  getStatusLabel(status: string | null): string {
    const normalizedStatus = (status ?? '').trim().toLowerCase();
    if (
      !normalizedStatus ||
      normalizedStatus === 'submitted' ||
      normalizedStatus === 'under_scrutiny'
    ) {
      return 'Under Scrutiny';
    }
    if (normalizedStatus.includes('accept')) {
      return 'Accepted';
    }
    if (normalizedStatus.includes('reject') || normalizedStatus.includes('object')) {
      return 'Rejected';
    }
    return status ?? 'Under Scrutiny';
  }

  getStatusBadgeClass(status: string | null): string {
    const label = this.getStatusLabel(status).toLowerCase();
    if (label.includes('accept')) {
      return 'background: #dcfce7; color: #166534';
    }
    if (label.includes('reject')) {
      return 'background: #fee2e2; color: #991b1b';
    }
    return 'background: #fef3c7; color: #92400e';
  }
}
