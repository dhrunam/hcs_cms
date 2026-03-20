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
import Swal from 'sweetalert2';
import { ActivatedRoute, Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { HttpEventType } from '@angular/common/http';

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
  isUploadingDocuments = false;
  uploadFileProgresses: number[] = [];
  uploadCompletedToken = 0;
  caseDetailsLocked = false;
  caseDetailsData: any = null;
  filingData: any = null;

  form!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private toastr: ToastrService,
    private eFilingService: EfilingService,
    private route: ActivatedRoute,
    private router: Router,
  ) {
    this.form = this.fb.group({
      initialInputs: this.fb.group({
        bench: ['High Court Of Sikkim', Validators.required],
        case_type: ['', Validators.required],
        petitioner_name: ['', Validators.required],
        petitioner_contact: ['', [Validators.required, Validators.pattern(/^[0-9]{10}$/)]],
        e_filing_number: [this.eFilingNumber],
      }),

      litigants: this.fb.group(
        {
          name: ['', Validators.required],
          gender: [''],
          age: [''],

          sequence_number: ['', Validators.required],

          is_diffentially_abled: [false],
          is_petitioner: [true],

          is_organisation: [false],
          organization: [''],

          contact: ['', [Validators.pattern(/^[0-9]{10}$/)]],
          email: ['', [Validators.email]],

          religion: [''],
          caste: [''],
          occupation: [''],

          address: ['', Validators.required],

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
            const gender = group.get('gender')?.value;

            if (isOrg && !org) {
              return { orgRequired: true };
            }

            if (!isOrg && !age) {
              return { ageRequired: true };
            }

            if (!isOrg && !gender) {
              return { genderRequired: true };
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
      const idParam = params['id'] ?? params['efiling_id'] ?? params['e_filing_id'];
      this.filingId = Number(idParam || 0) || null;
      this.eFilingNumber = params['e_filing_number'] || this.eFilingNumber;
      if (this.filingId) {
        this.loadInitialInputs();
        this.loadCaseDetails();
        this.loadActList();
      }
    });
  }

  actList: any[] = [];

  receiveActList(data: any[]) {
    this.actList = [...this.actList, ...data];
    const shouldPersistActs =
      !!this.filingId &&
      (this.step3Saved || this.caseDetailsForm.disabled || this.caseDetailsLocked);

    if (shouldPersistActs) {
      data.forEach((item: any) => {
        const payload = new FormData();

        payload.append('e_filing', String(this.filingId));
        payload.append('e_filing_number', this.eFilingNumber);
        payload.append('act', item.act);
        payload.append('section', item.section);

        this.eFilingService.add_case_details_act(payload).subscribe(() => {
          this.loadActList();
        });
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

  removeAct(index: number) {
    const act = this.actList[index];
    if (act?.id && this.filingId) {
      this.eFilingService.delete_case_details_act(act.id).subscribe(() => {
        this.actList = this.actList.filter((_: any, i: number) => i !== index);
      });
      return;
    }

    this.actList = this.actList.filter((_: any, i: number) => i !== index);
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
    const isCaseDetailsStep = this.step === 3;

    if (this.step === 2 && !this.hasRequiredLitigants()) {
      const message = this.hasPetitionerOnly()
        ? 'At least one respondent should be added.'
        : 'Please complete the form before continuing.';
      this.toastr.error(message, '', {
        timeOut: 3000,
        closeButton: true,
      });
      return;
    }

    if (this.step == 2 && this.litigantList.length > 0) {
      this.step++;
    }

    if (this.step == 4 && this.docList.length > 0) {
      this.step++;
    }

    if (isCaseDetailsStep) {
      if (!this.step3Saved) {
        this.saveStep3();
        return;
      }
    } else if (currentForm.invalid) {
      currentForm.markAllAsTouched();
      return;
    }

    if (this.step < 5) {
      this.step++;
    }

    this.setCaseDetailsReviewState(this.step === 5);

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  prev() {
    if (this.step > 1) {
      this.step--;
    }

    this.setCaseDetailsReviewState(this.step === 5);
  }

  goToStep(stepNumber: number) {
    const maxStep = this.getMaxAllowedStep();
    if (stepNumber > maxStep) {
      this.toastr.error('Please complete the current form before moving forward.', '', {
        timeOut: 3000,
        closeButton: true,
      });
      return;
    }

    this.step = stepNumber;
    this.setCaseDetailsReviewState(this.step === 5);
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
        timeOut: 3000,
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

    if (!this.isSequenceNumberUnique(formValue.sequence_number, formValue.is_petitioner)) {
      const typeLabel = this.getLitigantTypeLabel(formValue.is_petitioner);
      this.toastr.error(`Sequence number must be unique for ${typeLabel}.`, '', {
        timeOut: 3000,
      });
      form.get('sequence_number')?.markAsTouched();
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    if (formValue.is_organisation) {
      formValue.age = 0;
    }

    if (form.invalid) {
      form.markAllAsTouched();
      window.scrollTo({ top: 0, behavior: 'smooth' });
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

      form.reset({
        is_diffentially_abled: false,
        is_petitioner: formValue.is_petitioner,
        sequence_number: '',
        gender: '',
        organization: '',
      });

      window.scrollTo({ top: 0, behavior: 'smooth' });

      const typeLabel = this.getLitigantTypeLabel(formValue.is_petitioner);
      this.toastr.success(`1 ${typeLabel} added`, '', {
        timeOut: 3000,
      });
    });
  }

  onDelete(id: number) {
    this.litigantList = this.litigantList.filter((item) => item.id !== id);
  }

  private isSequenceNumberUnique(sequenceNumber: number, isPetitioner: boolean): boolean {
    if (!sequenceNumber && sequenceNumber !== 0) return false;
    return !this.litigantList.some(
      (item) =>
        this.normalizeIsPetitioner(item.is_petitioner) ===
          this.normalizeIsPetitioner(isPetitioner) &&
        Number(item.sequence_number) === Number(sequenceNumber),
    );
  }

  private normalizeIsPetitioner(value: any): boolean {
    return value === true || value === 'true' || value === 1 || value === '1';
  }

  private getLitigantTypeLabel(isPetitioner: boolean): string {
    return this.normalizeIsPetitioner(isPetitioner) ? 'petitioner' : 'respondent';
  }

  private getNextSequenceNumber(isPetitioner: boolean): number {
    const maxSequence = this.litigantList
      .filter((item) => item.is_petitioner === isPetitioner)
      .reduce((max, item) => Math.max(max, Number(item.sequence_number) || 0), 0);
    return maxSequence + 1;
  }

  private hasPetitionerOnly(): boolean {
    const hasPetitioner = this.litigantList.some((item) => item.is_petitioner);
    const hasRespondent = this.litigantList.some((item) => !item.is_petitioner);
    return hasPetitioner && !hasRespondent;
  }

  updateStep2() {}

  saveStep3() {
    const form = this.caseDetailsForm;

    form.markAllAsTouched();

    const missingRequiredActs = this.actList.length === 0;
    const missingRequiredDetails =
      form.get('cause_of_action')?.invalid || form.get('date_of_cause_of_action')?.invalid;

    if (missingRequiredActs || missingRequiredDetails) {
      this.toastr.error('Please add at least one act and complete required fields.', '', {
        timeOut: 3000,
      });
      if (missingRequiredDetails) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
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
      this.step3Saved = true;
      this.caseDetailsLocked = true;
      this.caseDetailsForm.disable({ emitEvent: false });
      this.caseDetailsForm.get('act')?.enable({ emitEvent: false });
      this.caseDetailsForm.get('section')?.enable({ emitEvent: false });
      this.step = 4;
    });
  }

  hasRequiredLitigants(): boolean {
    const hasPetitioner = this.litigantList.some((item) => item.is_petitioner);
    const hasRespondent = this.litigantList.some((item) => !item.is_petitioner);
    return hasPetitioner && hasRespondent;
  }

  isCaseDetailsNextDisabled(): boolean {
    const form = this.caseDetailsForm;
    const hasCause = !form.get('cause_of_action')?.invalid;
    const hasDate = !form.get('date_of_cause_of_action')?.invalid;
    const hasActs = this.actList.length > 0;
    return !hasCause || !hasDate || !hasActs;
  }

  private getMaxAllowedStep(): number {
    if (!this.eFilingNumber) return 1;
    if (!this.hasRequiredLitigants()) return 2;
    if (!this.step3Saved) return 3;
    return 5;
  }

  goToPageFromPreview(step: number) {
    this.step = step;
    this.setCaseDetailsReviewState(this.step === 5);
  }

  private loadCaseDetails() {
    this.eFilingService.get_case_details_by_filing_id(this.filingId || 0).subscribe({
      next: (data) => {
        const details = Array.isArray(data?.results) ? data.results[0] : data;
        if (!details) return;

        this.caseDetailsData = details;

        this.caseDetailsForm.patchValue({
          cause_of_action: details.cause_of_action || '',
          date_of_cause_of_action: details.date_of_cause_of_action || '',
          dispute_state: details.dispute_state || '',
          dispute_district: details.dispute_district || '',
          dispute_taluka: details.dispute_taluka || '',
          act: '',
          section: '',
        });

        this.step3Saved = true;
        this.caseDetailsLocked = true;
        this.caseDetailsForm.disable({ emitEvent: false });
        this.caseDetailsForm.get('act')?.enable({ emitEvent: false });
        this.caseDetailsForm.get('section')?.enable({ emitEvent: false });
      },
    });
  }

  private loadInitialInputs() {
    this.eFilingService.get_filing_by_efiling_id(this.filingId || 0).subscribe({
      next: (data) => {
        const record = Array.isArray(data?.results) ? data.results[0] : data;
        if (!record) return;

        this.filingData = record;

        this.initialInputsForm.patchValue({
          bench: record.bench || 'High Court Of Sikkim',
          case_type: record.case_type || '',
          petitioner_name: record.petitioner_name || '',
          petitioner_contact: record.petitioner_contact || '',
          e_filing_number: record.e_filing_number || this.eFilingNumber,
        });
        if (record.e_filing_number) {
          this.eFilingNumber = record.e_filing_number;
        }
        this.step1Saved = true;
        this.initialInputsForm.disable({ emitEvent: false });
      },
    });
  }

  private loadActList() {
    this.eFilingService.get_acts_by_filing_id(this.filingId || 0).subscribe({
      next: (data) => {
        const rows = Array.isArray(data?.results) ? data.results : [];
        this.actList = rows.map((item: any) => ({
          id: item.id,
          act: item.act,
          actname:
            item.actname ||
            item.act_name ||
            item.act?.actname ||
            item.act?.act_name ||
            item.act?.act ||
            item.act,
          section: item.section,
        }));
      },
    });
  }

  private setCaseDetailsReviewState(isReview: boolean) {
    const form = this.caseDetailsForm;
    if (!form) return;

    if (isReview || this.caseDetailsLocked) {
      form.disable({ emitEvent: false });
      form.get('act')?.enable({ emitEvent: false });
      form.get('section')?.enable({ emitEvent: false });
      return;
    }

    form.enable({ emitEvent: false });
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

  async handleDocUpload(data: any) {
    const documentType = String(data?.document_type || '').trim();
    const uploadItems = Array.isArray(data?.items) ? data.items : [];

    if (!documentType || uploadItems.length === 0 || !this.filingId) return;

    this.isUploadingDocuments = true;
    this.uploadFileProgresses = uploadItems.map(() => 0);

    try {
      const documentPayload = new FormData();
      documentPayload.append('document_type', documentType);
      documentPayload.append('e_filing', String(this.filingId));
      documentPayload.append('e_filing_number', this.eFilingNumber);

      const documentRes = await firstValueFrom(
        this.eFilingService.upload_case_documnets(documentPayload),
      );

      const documentId = documentRes?.id;
      if (!documentId) return;

      const uploadedDocumentParts: any[] = [];

      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];
        const indexPayload = new FormData();
        indexPayload.append('document', String(documentId));
        indexPayload.append('document_part_name', String(item.index_name || '').trim());
        indexPayload.append('file_part_path', item.file);
        indexPayload.append('document_sequence', String(i + 1));
        if (item.index_id) {
          indexPayload.append('index', String(item.index_id));
        }

        const indexRes = await this.uploadIndexFileWithProgress(indexPayload, i);
        uploadedDocumentParts.push(indexRes);
      }

      this.docList.push({
        ...documentRes,
        document_indexes: uploadedDocumentParts,
        final_document: uploadedDocumentParts[0]?.file_url || documentRes?.final_document,
      });
      this.uploadCompletedToken++;
    } catch (error) {
      console.error('Document upload failed', error);
    } finally {
      this.isUploadingDocuments = false;
    }
  }

  private uploadIndexFileWithProgress(formData: FormData, index: number): Promise<any> {
    return new Promise((resolve, reject) => {
      this.eFilingService.upload_case_documnets_index(formData).subscribe({
        next: (event: any) => {
          if (event.type === HttpEventType.UploadProgress) {
            const total = event.total || 0;
            if (total > 0) {
              this.uploadFileProgresses[index] = Math.round((event.loaded / total) * 100);
            }
          }

          if (event.type === HttpEventType.Response) {
            this.uploadFileProgresses[index] = 100;
            resolve(event.body);
          }
        },
        error: (err) => reject(err),
      });
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
        this.toastr.success('OTP has been sent successfully.', '', {
          timeOut: 3000,
          closeButton: true,
        });

        this.promptOtpAndSubmit();
      }
    });
  }

  private promptOtpAndSubmit() {
    if (!this.filingId) return;

    let submitting = false;

    Swal.fire({
      title: 'Enter OTP',
      html:
        '<div style="display:flex;gap:8px;justify-content:center">' +
        ['otp-1', 'otp-2', 'otp-3', 'otp-4']
          .map(
            (id) =>
              `<input id="${id}" type="text" inputmode="numeric" maxlength="1" style="width:48px;height:48px;text-align:center;font-size:20px;border:1px solid #d1d5db;border-radius:8px;" />`,
          )
          .join('') +
        '</div>' +
        '<div id="otp-status" style="margin-top:12px;font-size:14px;text-align:center"></div>',
      showCancelButton: true,
      showConfirmButton: false,
      allowOutsideClick: false,
      didOpen: () => {
        const ids = ['otp-1', 'otp-2', 'otp-3', 'otp-4'];
        const inputs = ids
          .map((id) => document.getElementById(id) as HTMLInputElement | null)
          .filter((el): el is HTMLInputElement => !!el);
        const statusEl = document.getElementById('otp-status');

        const setStatus = (message: string, color: string) => {
          if (!statusEl) return;
          statusEl.textContent = message;
          statusEl.style.color = color;
        };

        const getOtp = () => inputs.map((el) => el.value || '').join('');

        const validateOtp = () => {
          const otp = getOtp();
          if (otp.length < 4) {
            setStatus('', '');
            return;
          }

          if (otp !== '0000') {
            setStatus('OTP error. Please try again.', '#dc2626');
            return;
          }

          setStatus('OTP verified.', '#16a34a');
          if (submitting) return;
          submitting = true;

          this.eFilingService.final_submit_efiling(this.filingId || 0).subscribe({
            next: () => {
              Swal.fire({
                icon: 'success',
                title: 'Filed Successfully',
                text: 'Your filing has been submitted for scrutiny.',
              }).then(() => {
                this.router.navigate(['/advocate/dashboard/efiling/pending-scrutiny']);
              });
            },
            error: (err) => {
              submitting = false;
              setStatus('Submission failed. Please try again.', '#dc2626');
              console.error(err);
            },
          });
        };

        inputs.forEach((input, index) => {
          input.addEventListener('input', () => {
            input.value = input.value.replace(/\D/g, '').slice(0, 1);
            if (input.value && inputs[index + 1]) inputs[index + 1].focus();
            validateOtp();
          });

          input.addEventListener('keydown', (event) => {
            if (event.key === 'Backspace' && !input.value && inputs[index - 1]) {
              inputs[index - 1].focus();
            }
          });
        });

        inputs[0]?.focus();
      },
    });
  }
}
