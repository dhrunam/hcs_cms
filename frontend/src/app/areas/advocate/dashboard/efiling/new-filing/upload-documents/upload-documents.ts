import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-upload-documents',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './upload-documents.html',
  styleUrl: './upload-documents.css',
})
export class UploadDocuments {
  @Input() form!: FormGroup;
  @Input() litigantList!: any;

  onFileChange(event: any) {
    const files = Array.from(event.target.files);
    this.form.get('uploadFilingDoc.documents')?.setValue(files);
  }
}
