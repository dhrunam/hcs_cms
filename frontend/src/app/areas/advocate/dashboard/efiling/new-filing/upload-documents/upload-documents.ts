import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-upload-documents',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './upload-documents.html',
})
export class UploadDocuments {
  @Output() submitDoc = new EventEmitter<any>();
  @Input() form!: FormGroup;

  selectedFile!: File;

  constructor() {}

  onFileChange(event: any) {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      this.selectedFile = file;
      this.form.patchValue({ final_document: file });
    }
  }

  submit() {
    if (this.form.invalid) return;

    const payload = {
      document_type: this.form.value.document_type,
      file: this.selectedFile,
    };

    this.submitDoc.emit(payload);
  }
}
