import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

interface DraftFiling {
  id: number;
  caseTitle: string;
  filingType: string;
  lastUpdated: string;
  bench: string;
}

@Component({
  selector: 'app-draft-filings',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './draft-filings.html',
  styleUrls: ['./draft-filings.css'],
})
export class DraftFilings {
  drafts: DraftFiling[] = [
    {
      id: 1,
      caseTitle: 'Sample draft case',
      filingType: 'Petition',
      lastUpdated: '12 Mar 2026',
      bench: 'Bench A',
    },
  ];

  get hasDrafts(): boolean {
    return this.drafts.length > 0;
  }
}

