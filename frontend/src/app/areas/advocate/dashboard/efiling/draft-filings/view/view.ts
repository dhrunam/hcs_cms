import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
interface DraftFiling {
  id: number;
  caseTitle: string;
  filingType: string;
  lastUpdated: string;
  bench: string;
}

@Component({
  selector: 'app-view',
  imports: [RouterModule],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class View {
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
