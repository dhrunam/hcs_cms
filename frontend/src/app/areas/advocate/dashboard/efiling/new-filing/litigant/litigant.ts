import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-litigant',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './litigant.html',
  styleUrl: './litigant.css',
})
export class Litigant {
  @Input() form!: FormGroup;
}
