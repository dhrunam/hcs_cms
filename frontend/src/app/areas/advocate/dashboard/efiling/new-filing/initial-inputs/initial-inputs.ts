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
  @Input() isDraft = false;
  case_types: any[] = [];

  ngOnInit() {
    this.get_case_types();
  }

  get_case_types() {
    this.caseTypeService.get_case_types().subscribe({
      next: (data) => {
        this.case_types = data;
      },
    });
  }

  get_case_type_label(value: any): string {
    if (value?.type_name) return value.type_name;
    const id = value?.id ?? value;
    return this.case_types.find((item) => item.id === id)?.type_name || '';
  }
}
