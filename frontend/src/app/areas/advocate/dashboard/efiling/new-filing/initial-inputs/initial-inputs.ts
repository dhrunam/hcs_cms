import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { CaseTypeService } from '../../../../../../services/master/case-type.services';

@Component({
  selector: 'app-initial-inputs',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './initial-inputs.html',
  styleUrl: './initial-inputs.css',
})
export class InitialInputs {
  constructor(private caseTypeService: CaseTypeService) {}

  @Input() form!: FormGroup;
  case_types: any[] = [];

  ngOnInit() {
    this.get_case_types();
  }

  get_case_types() {
    this.caseTypeService.get_case_types().subscribe({
      next: (data) => {
        this.case_types = data.results;
      },
    });
  }
}
