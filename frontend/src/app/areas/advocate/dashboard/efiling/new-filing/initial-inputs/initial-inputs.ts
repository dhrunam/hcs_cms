import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-initial-inputs',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './initial-inputs.html',
  styleUrl: './initial-inputs.css',
})
export class InitialInputs {
  @Input() form!: FormGroup;
}
