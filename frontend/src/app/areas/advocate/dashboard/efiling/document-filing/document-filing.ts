import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-document-filing',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './document-filing.html',
  styleUrls: ['./document-filing.css'],
})
export class DocumentFiling {
}

