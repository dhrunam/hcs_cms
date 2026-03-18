import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-draft-filings',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './draft-filings.html',
  styleUrls: ['./draft-filings.css'],
})
export class DraftFilings {
}

