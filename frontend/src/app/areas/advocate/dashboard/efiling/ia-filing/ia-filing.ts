import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-ia-filing',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './ia-filing.html',
  styleUrls: ['./ia-filing.css'],
})
export class IaFiling {}
