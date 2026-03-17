import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'app-e-file',
  imports: [],
  templateUrl: './e-file.html',
  styleUrl: './e-file.css',
})
export class EFile {
  @Input() form!: FormGroup;

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
