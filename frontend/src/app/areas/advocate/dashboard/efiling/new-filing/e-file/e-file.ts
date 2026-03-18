import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { CaseTypeService } from '../../../../../../services/master/case-type.services';

@Component({
  selector: 'app-e-file',
  imports: [CommonModule],
  templateUrl: './e-file.html',
  styleUrl: './e-file.css',
})
export class EFile {
  @Input() form!: FormGroup;
  @Input() litigantList!: any;
  caseTypes: any[] = [];

  constructor(private caseTypeService: CaseTypeService) {}

  ngOnInit() {}

  get_case_types() {
    this.caseTypeService.get_case_types().subscribe({
      next: (data) => {
        this.caseTypes = data.results;
      },
    });
  }

  get_case_type_name(id: number): string {
    return this.caseTypes.find((n) => n.id === id)?.name || '';
  }

  get initialInputsForm(): FormGroup {
    return this.form.get('initialInputs') as FormGroup;
  }

  get litigantsForm(): FormGroup {
    return this.form.get('litigants') as FormGroup;
  }

  get caseDetailsForm(): FormGroup {
    return this.form.get('caseDetails') as FormGroup;
  }
}
