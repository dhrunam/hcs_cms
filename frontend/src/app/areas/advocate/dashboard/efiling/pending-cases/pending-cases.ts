import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

interface PendingCase {
  id: number;
  caseTitle: string;
  filingType: string;
  filedOn: string;
  status: string;
}

@Component({
  selector: 'app-pending-cases',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pending-cases.html',
  styleUrls: ['./pending-cases.css'],
})
export class PendingCases {
  cases: PendingCase[] = [];

  get hasCases(): boolean {
    return this.cases.length > 0;
  }
}

