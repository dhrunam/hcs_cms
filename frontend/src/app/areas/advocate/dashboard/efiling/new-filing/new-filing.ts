import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';

import { InitialInputs } from './initial-inputs/initial-inputs';
import { Litigant } from './litigant/litigant';
import { CaseDetails } from './case-details/case-details';
import { EfilingService } from '../../../../../services/advocate/efiling/efiling.services';
import { EFile } from './e-file/e-file';
import { UploadDocuments } from './upload-documents/upload-documents';

@Component({
  selector: 'app-new-filing',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    InitialInputs,
    Litigant,
    CaseDetails,
    EFile,
    UploadDocuments,
  ],
  templateUrl: './new-filing.html',
  styleUrls: ['./new-filing.css'],
})
export class NewFiling {
  step = 1;
  // filingId: number | null = null;
  // eFilingNumber: string = '';
  filingId: number = 4;
  eFilingNumber: string = 'ASK20240000004C202600004';
  step1Saved = false;
  step2Saved = false;
  step3Saved = false;
  litigantList: any[] = [];
  sequenceNumber_litigant: number = 1;
  isUpdateMode = false;

  form!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private toastr: ToastrService,
    private eFilingService: EfilingService,
  ) {
    this.form = this.fb.group({
      initialInputs: this.fb.group({
        bench: ['High Court Of Sikkim', Validators.required],
        case_type: ['', Validators.required],
        petitioner_name: ['', Validators.required],
        petitioner_contact: ['', Validators.required],
        e_filing_number: [this.eFilingNumber],
      }),

      litigants: this.fb.group(
        {
          name: ['', Validators.required],
          gender: [''],
          age: [''],

          sequence_number: [1, Validators.required],

          is_diffentially_abled: [false],
          is_petitioner: [true],

          is_organisation: [false],
          organization: [''],

          contact: [''],
          email: [''],

          religion: [''],
          caste: [''],
          occupation: [''],

          address: [''],

          state_id: [''],
          district_id: [''],

          taluka: [''],
          village: [''],
        },

        {
          validators: (group) => {
            const isOrg = group.get('is_organisation')?.value;
            const org = group.get('organization')?.value;
            const age = group.get('age')?.value;

            if (isOrg && !org) {
              return { orgRequired: true };
            }

            if (!isOrg && !age) {
              return { ageRequired: true };
            }

            return null;
          },
        },
      ),

      caseDetails: this.fb.group({
        causeOfAction: ['', Validators.required],
        causeOfActionDate: ['', Validators.required],
        state: [''],
        district: [''],
        taluka: [''],
        hobli: [''],

        act: ['', Validators.required],
        section: ['', Validators.required],
      }),

      uploadFilingDoc: this.fb.group({
        documents: [[], [Validators.required, this.pdfOnlyValidator]],
      }),
    });
  }

  actList: any[] = [];

  receiveActList(data: any[]) {
    this.actList = data;

    console.log('Act list inm parent page', this.actList);

    const group = this.form.get('caseDetails') as FormGroup;

    group.patchValue({
      act: '',
      section: '',
    });

    group.get('act')?.markAsPristine();
    group.get('act')?.markAsUntouched();
    group.get('section')?.markAsPristine();
    group.get('section')?.markAsUntouched();
  }

  pdfOnlyValidator(control: any) {
    const files: File[] = control.value;

    if (!files || files.length === 0) return null;

    const invalid = files.some((file) => file.type !== 'application/pdf');

    return invalid ? { invalidFileType: true } : null;
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

  getCurrentForm(): FormGroup {
    if (this.step === 1) {
      return this.form.get('initialInputs') as FormGroup;
    }

    if (this.step === 2) {
      return this.form.get('litigants') as FormGroup;
    }

    if (this.step === 3) {
      return this.form.get('caseDetails') as FormGroup;
    }

    return this.form;
  }

  next() {
    const currentForm = this.getCurrentForm();

    if (this.step == 2 && this.litigantList.length > 0) {
      this.step++;
    }

    if (currentForm.invalid) {
      currentForm.markAllAsTouched();
      return;
    }

    if (this.step < 4) {
      this.step++;
    }

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  prev() {
    if (this.step > 1) {
      this.step--;
    }
  }

  goToStep(stepNumber: number) {
    // if (stepNumber <= this.step) {
    //   this.step = stepNumber;
    // }
    this.step = stepNumber;
  }

  saveStep1() {
    const form = this.form.get('initialInputs') as FormGroup;

    if (form.invalid) {
      form.markAllAsTouched();
      return;
    }

    this.eFilingService.post_efiling_initial_details(form.value).subscribe((res: any) => {
      this.filingId = res.id;
      this.eFilingNumber = res.e_filing_number;
      this.form.get('initialInputs')?.patchValue({
        e_filing_number: this.eFilingNumber,
      });
      this.initialInputsForm.disable();
      this.step = 2;
      this.toastr.success('Saved successfully. E Filing number: ' + this.eFilingNumber, '', {
        timeOut: 11000,
        closeButton: true,
        progressBar: true,
        positionClass: 'toast-bottom-right',
      });
    });
  }

  // saveStep2() {
  //   const form = this.form.get('litigants') as FormGroup;

  //   if (form.invalid) {
  //     form.markAllAsTouched();
  //     return;
  //   }

  //   const payload = {
  //     ...form.value,
  //     e_filing: this.filingId,
  //     e_filing_number: this.eFilingNumber,
  //   };

  //   this.eFilingService.post_litigant_details(payload).subscribe((res: any) => {
  //     this.step = 3;
  //     this.step2Saved = true;

  //     this.toastr.success('Litigant Details saved successfully', '', {
  //       timeOut: 5000,
  //       closeButton: true,
  //       progressBar: true,
  //       positionClass: 'toast-bottom-right',
  //     });
  //   });
  // }

  saveStep2() {
    const form = this.form.get('litigants') as FormGroup;
    const formValue = { ...form.value };

    if (formValue.is_organisation) {
      formValue.age = 0;
    }

    if (form.invalid) {
      form.markAllAsTouched();
      return;
    }

    const payload = {
      ...formValue,
      e_filing: this.filingId,
      e_filing_number: this.eFilingNumber,
    };

    this.eFilingService.post_litigant_details(payload).subscribe((res: any) => {
      this.litigantList.push(res);

      console.log('Litigant details are', res);

      this.sequenceNumber_litigant++;

      form.reset({
        is_diffentially_abled: false,
        is_petitioner: true,
        sequence_number: this.sequenceNumber_litigant, // 👈 set here
      });

      window.scrollTo({ top: 0, behavior: 'smooth' });

      this.toastr.success('Litigant added to table', '', {
        timeOut: 3000,
      });
    });
  }

  onDelete(id: number) {
    this.litigantList = this.litigantList.filter((item) => item.id !== id);
  }

  updateStep2() {}

  saveStep3() {
    const form = this.caseDetailsForm;

    if (this.actList.length === 0 && (!form.value.act || !form.value.section)) {
      form.markAllAsTouched();
      return;
    }

    const acts = this.actList.length
      ? this.actList
      : [{ act: form.value.act, section: form.value.section }];

    const payload = {
      ...form.value,
      e_filing: this.filingId,
      e_filing_number: this.eFilingNumber,
      efiling_acts: acts.map((a) => ({
        ...a,
        e_filing: this.filingId,
        e_filing_number: this.eFilingNumber,
      })),
    };

    this.eFilingService.post_case_details(payload).subscribe(() => {
      this.step = 4;
    });
  }

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const formData = this.form.value;

    console.log(formData);
  }
}
