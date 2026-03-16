import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-case-details',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './case-details.html',
  styleUrl: './case-details.css',
})
export class CaseDetails {
  @Input() form!: FormGroup;
}
