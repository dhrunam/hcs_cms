import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import Swal from 'sweetalert2';

import { CourtroomService } from '../../../../services/judge/courtroom.service';

@Component({
  selector: 'app-judge-courtroom',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './courtroom.html',
  styleUrl: './courtroom.css',
})
export class JudgeCourtroomPage {
  efilingId: number | null = null;
  forwardedForDate: string | null = null;

  isLoading = false;
  loadError = '';

  documents: any[] = [];
  selectedDoc: any = null;

  listingDate: string = new Date().toISOString().slice(0, 10);
  approved = false;
  decisionNotes = '';

  canWrite = false;
  selectedDocUrl: SafeResourceUrl | null = null;

  constructor(
    private route: ActivatedRoute,
    private courtroomService: CourtroomService,
    private sanitizer: DomSanitizer,
  ) {}

  ngOnInit(): void {
    this.canWrite = this.readCanWrite();

    const idRaw = this.route.snapshot.paramMap.get('id');
    this.efilingId = idRaw ? Number(idRaw) : null;

    this.forwardedForDate = this.route.snapshot.queryParamMap.get('forwarded_for_date');
    if (!this.efilingId || !this.forwardedForDate) {
      this.loadError = 'Missing case id or forwarded_for_date.';
      return;
    }

    this.loadCaseDocuments();
  }

  private readCanWrite(): boolean {
    try {
      const raw = sessionStorage.getItem('user_groups');
      const groups = raw ? JSON.parse(raw) : [];
      return Array.isArray(groups) && groups.some((g) => ['JUDGE_CJ', 'JUDGE_J1', 'JUDGE_J2'].includes(String(g)));
    } catch {
      return false;
    }
  }

  private loadCaseDocuments(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.isLoading = true;
    this.loadError = '';

    this.courtroomService.getCaseDocuments(this.efilingId, this.forwardedForDate).subscribe({
      next: (resp) => {
        this.documents = resp?.items ?? [];
        this.selectedDoc = this.documents[0] ?? null;
        this.selectedDocUrl = this.selectedDoc?.file_url
          ? this.sanitizer.bypassSecurityTrustResourceUrl(this.selectedDoc.file_url)
          : null;
        this.isLoading = false;
      },
      error: (err) => {
        console.warn('Failed to load courtroom documents', err);
        this.loadError = 'Failed to load documents.';
        this.isLoading = false;
      },
    });
  }

  selectDocument(doc: any): void {
    this.selectedDoc = doc;
    if (doc?.file_url) {
      this.selectedDocUrl = this.sanitizer.bypassSecurityTrustResourceUrl(doc.file_url);
    } else {
      this.selectedDocUrl = null;
    }
  }

  trackByDocId(_index: number, doc: any): number {
    return Number(doc?.id ?? 0);
  }

  saveAnnotation(doc: any): void {
    if (!this.canWrite || !doc?.id) return;
    this.courtroomService
      .saveDocumentAnnotation({
        efiling_document_index_id: doc.id,
        annotation_text: doc.annotation_text ?? '',
      })
      .subscribe({
        next: () => {
          Swal.fire({ title: 'Saved', text: 'Annotation saved.', icon: 'success', timer: 800, showConfirmButton: false });
        },
        error: (err) => {
          console.warn('save annotation failed', err);
          Swal.fire({ title: 'Error', text: 'Failed to save annotation.', icon: 'error' });
        },
      });
  }

  submitDecision(): void {
    if (!this.canWrite || !this.efilingId || !this.forwardedForDate || !this.listingDate) return;
    Swal.fire({
      title: 'Save decision?',
      text: 'Are you sure you want to approve/reject this case for listing?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, save',
    }).then((res) => {
      if (!res.isConfirmed) return;

      this.courtroomService
        .saveDecision({
          efiling_id: this.efilingId!,
          forwarded_for_date: this.forwardedForDate!,
          listing_date: this.listingDate,
          approved: this.approved,
          decision_notes: this.decisionNotes || null,
        })
        .subscribe({
          next: () => {
            Swal.fire({ title: 'Saved', text: 'Decision saved.', icon: 'success', timer: 1000, showConfirmButton: false });
          },
          error: (err) => {
            console.warn('save decision failed', err);
            Swal.fire({ title: 'Error', text: 'Failed to save decision.', icon: 'error' });
          },
        });
    });
  }
}

