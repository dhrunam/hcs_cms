import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
interface PendingCase {
  id: number;
  caseTitle: string;
  filingType: string;
  filedOn: string;
  status: string;
}

@Component({
  selector: 'app-view',
  imports: [CommonModule, RouterLink],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class View {
  filingsUnderDraft: any[] | null = null;

  constructor(private eFilingService: EfilingService) {}

  ngOnInit() {
    this.get_filings_under_scrutiny();
  }

  get_filings_under_scrutiny() {
    this.eFilingService.get_filings_under_draft().subscribe({
      next: (data) => {
        this.filingsUnderDraft = data.results;
        console.log(this.filingsUnderDraft);
      },
    });
  }
}
