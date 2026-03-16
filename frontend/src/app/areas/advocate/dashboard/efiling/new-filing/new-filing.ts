import { CommonModule } from '@angular/common';
import { ToastrService } from 'ngx-toastr';
import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { InitialInputs } from './initial-inputs/initial-inputs';
import { Litigant } from './litigant/litigant';
import { CaseDetails } from './case-details/case-details';

@Component({
  selector: 'app-new-filing',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, InitialInputs, Litigant, CaseDetails],
  templateUrl: './new-filing.html',
  styleUrls: ['./new-filing.css'],
})
export class NewFiling {
  step = 1;

  initialInputs!: FormGroup;
  litigants!: FormGroup;
  // step3!: FormGroup;
  stepCaseDetails!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private toastr: ToastrService,
  ) {
    this.initialInputs = this.fb.group({
      bench: ['', Validators.required],

      nature: ['', Validators.required],
      // relief: ['', Validators.required],
      // caseType: ['', Validators.required],

      // status: ['', Validators.required],
      // mainCaseType: ['', Validators.required],
      // caseNo: ['', Validators.required],
      // year: ['', Validators.required],

      partyType: ['', Validators.required],
      mobile: ['', Validators.required],
    });

    this.litigants = this.fb.group({
      litigantType: ['petitioner', Validators.required],
      isOrganisation: [false],
      organisationType: ['', Validators.required],
      litigantName: ['', [Validators.required, Validators.minLength(3)]],

      email: ['', [Validators.required, Validators.email]],
      mobile: ['', Validators.required],
      occupation: [''],
      address: ['', Validators.required],
      pincode: ['', Validators.required],

      state: [''],
      district: [''],
      taluka: [''],
      hobli: [''],

      otherInformation: [false],
      legalHeir: [false],
    });

    // this.step3 = this.fb.group({
    //   address: ['', Validators.required],
    // });

    this.stepCaseDetails = this.fb.group({
      causeOfAction: ['', Validators.required],
      causeOfActionDate: ['', Validators.required],
      importantInformation: [''],
      prayer: [''],
      suitValuation: [''],

      plaintLocalLanguage: [false],

      state: [''],
      district: [''],
      taluka: [''],
      hobli: [''],

      act: ['', Validators.required],
      section: ['', Validators.required],
    });
  }

  next() {
    // if (this.step === 1 && this.step1.invalid) {
    //   this.step1.markAllAsTouched();
    //   return;
    // }

    // if (this.step === 2 && this.step2.invalid) {
    //   this.step2.markAllAsTouched();
    //   return;
    // }

    // if (this.step === 3 && this.step3.invalid) {
    //   this.step3.markAllAsTouched();
    //   return;
    // }
    // this.step++;

    if (this.step < 5) {
      this.step++;

      this.toastr.success('Changes saved successfully', '', {
        timeOut: 2000,
        closeButton: true,
        progressBar: true,
        positionClass: 'toast-bottom-right',
      });
      window.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
    }
  }

  prev() {
    if (this.step > 1) {
      this.step--;
    }
  }

  goToStep(stepNumber: number) {
    // if (stepNumber === 1) {
    //   this.step = 1;
    //   return;
    // }

    // if (stepNumber === 2 && this.step1.valid) {
    //   this.step = 2;
    // }

    // if (stepNumber === 3 && this.step1.valid && this.step2.valid) {
    //   this.step = 3;
    // }

    this.step = stepNumber;
  }

  submit() {
    // if (this.step3.invalid) {
    //   this.step3.markAllAsTouched();
    //   return;
    // }

    const formData = {
      ...this.initialInputs.value,
      ...this.litigants.value,
      // ...this.step3.value,
    };

    console.log(formData);
  }
}
