import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';

import Swal from 'sweetalert2';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { InitialInputs } from '../../new-filing/initial-inputs/initial-inputs';
import { Litigant } from '../../new-filing/litigant/litigant';
import { CaseDetails } from '../../new-filing/case-details/case-details';
import { EFile } from '../../new-filing/e-file/e-file';
import { UploadDocuments } from '../../new-filing/upload-documents/upload-documents';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';

@Component({
  selector: 'app-edit',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    InitialInputs,
    Litigant,
    CaseDetails,
    EFile,
    UploadDocuments,
    RouterLink,
  ],
  templateUrl: './edit.html',
  styleUrls: ['./edit.css'],
})
export class Edit {
  step = 2;
  filingId: number | null = null;
  eFilingNumber: string = '';
  // filingId: number = 28;
  // eFilingNumber: string = 'ASK20240000028C202600028';
  step1Saved = false;
  step2Saved = false;
  step3Saved = false;
  litigantList: any[] = [];
  sequenceNumber_litigant: number = 1;
  isUpdateMode = false;
  docList: any[] = [];
  isDeclarationChecked = false;

  form!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private toastr: ToastrService,
    private eFilingService: EfilingService,
    private route: ActivatedRoute,
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
        cause_of_action: ['', Validators.required],
        date_of_cause_of_action: ['', Validators.required],
        dispute_state: [''],
        dispute_district: [''],
        dispute_taluka: [''],

        act: ['', Validators.required],
        section: ['', Validators.required],
      }),

      actDetails: this.fb.group({
        act: ['', Validators.required],
        section: ['', Validators.required],
      }),

      uploadFilingDoc: this.fb.group({
        document_type: [null, Validators.required],
        final_document: [[], Validators.required],
      }),
      setDeclaration: this.fb.group({
        isDeclarationChecked: [false, Validators.requiredTrue],
      }),
    });
  }

  ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      this.filingId = params['id'];
      this.eFilingNumber = params['e_filing_number'];
      this.get_litigant_list_by_filing_id();
    });
  }

  get_litigant_list_by_filing_id() {
    this.eFilingService.get_litigant_list_by_filing_id(this.filingId || 0).subscribe({
      next: (data) => {
        this.litigantList = data.results;
      },
    });
  }

  actList: any[] = [];

  receiveActList(data: any[]) {
    this.actList = [...this.actList, ...data];
    if (this.caseDetailsForm.disabled) {
      data.forEach((item: any) => {
        const payload = new FormData();

        payload.append('e_filing', String(this.filingId));
        payload.append('e_filing_number', this.eFilingNumber);
        payload.append('act', item.act);
        payload.append('section', item.section);

        this.eFilingService.add_case_details_act(payload).subscribe();
      });
    }

    console.log('Act list in parent page', this.actList);

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

  getActDetailsForm(): FormGroup {
    return this.form.get('actDetails') as FormGroup;
  }

  get uploadFilingDocForm(): FormGroup {
    return this.form.get('uploadFilingDoc') as FormGroup;
  }

  get setDeclarationForm(): FormGroup {
    return this.form.get('setDeclaration') as FormGroup;
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

    if (this.step == 4 && this.docList.length > 0) {
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
        sequence_number: this.sequenceNumber_litigant,
        gender: '',
        organization: '',
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
      this.caseDetailsForm.disable();
    });
  }

  goToPageFromPreview(step: number) {
    this.step = step;
  }

  previewDoc(doc: any) {
    if (doc.final_document) {
      window.open(doc.final_document, '_blank');
    }
  }

  deleteDoc(id: number, index: number) {
    const confirmDelete = confirm(
      'Your document will be deleted and you need to re-upload it. Continue?',
    );

    if (!confirmDelete) return;

    this.eFilingService.delete_case_documnets_before_final_filing(id).subscribe({
      next: (res) => {
        console.log('Deleted response', res);
        this.docList.splice(index, 1);
      },
    });
  }

  handleDocUpload(data: any) {
    const formData = new FormData();
    formData.append('document_type', data.document_type);
    formData.append('final_document', data.file);
    formData.append('e_filing', this.filingId + '');
    formData.append('e_filing_number', this.eFilingNumber);

    this.eFilingService.upload_case_documnets(formData).subscribe({
      next: (res) => {
        console.log('After uploading documents', res);

        this.docList.push(res);
      },
    });
  }

  saveStep4() {
    const files = this.form.get('uploadFilingDoc.documents')?.value;

    if (!files || files.length === 0) return;

    const formData = new FormData();

    files.forEach((file: File, index: number) => {
      formData.append('documents', file); // same key for multiple
    });
  }

  submit() {
    Swal.fire({
      title: 'Submit Filing?',
      text: 'Once submitted, it will be forwarded for scrutiny.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, Submit',
      cancelButtonText: 'Cancel',
    }).then((result) => {
      if (result.isConfirmed) {
        const payload = {
          e_filing: this.filingId,
          e_filing_number: this.eFilingNumber,
        };

        this.eFilingService.final_submit_efiling(this.filingId || 0).subscribe({
          next: (res) => {
            Swal.fire({
              icon: 'success',
              title: 'Filed Successfully',
              text: 'Your filing has been submitted for scrutiny.',
            });

            console.log('Final submit response', res);
          },
          error: (err) => {
            Swal.fire({
              icon: 'error',
              title: 'Submission Failed',
              text: 'Something went wrong. Please try again.',
            });

            console.error(err);
          },
        });
      }
    });
  }
}
