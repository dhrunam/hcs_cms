import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
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

  caseSummary: any = null;

  listingDate: string = new Date().toISOString().slice(0, 10);
  decisionStatus: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS' = 'DECLINED';
  decisionNotes = '';
  requestedDocumentIds: number[] = [];

  canWrite = false;

  constructor(
    private route: ActivatedRoute,
    private courtroomService: CourtroomService,
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

    this.loadCaseSummary();
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

  private loadCaseSummary(): void {
    if (!this.efilingId || !this.forwardedForDate) return;
    this.isLoading = true;
    this.loadError = '';

    this.courtroomService.getCaseSummary(this.efilingId, this.forwardedForDate).subscribe({
      next: (resp) => {
        this.caseSummary = resp ?? null;
        this.forwardedForDate = resp?.forwarded_for_date ?? this.forwardedForDate;
        this.listingDate = resp?.forwarded_for_date ?? this.listingDate;
        const existingStatus = resp?.judge_decision?.status;
        if (existingStatus === 'APPROVED' || existingStatus === 'DECLINED' || existingStatus === 'REQUESTED_DOCS') {
          this.decisionStatus = existingStatus;
        }
        this.decisionNotes = resp?.judge_decision?.decision_notes ?? '';
        const requested = resp?.judge_decision?.requested_documents ?? [];
        this.requestedDocumentIds = Array.isArray(requested)
          ? requested.map((x: any) => Number(x?.document_index_id)).filter((x: number) => Number.isFinite(x))
          : [];
        this.isLoading = false;
      },
      error: (err) => {
        console.warn('Failed to load courtroom case summary', err);
        this.loadError = 'Failed to load case details.';
        this.isLoading = false;
      },
    });
  }

  submitDecision(): void {
    if (!this.canWrite || !this.efilingId || !this.forwardedForDate || !this.listingDate) return;
    if (this.decisionStatus === 'DECLINED' && !(this.decisionNotes || '').trim()) {
      Swal.fire({ title: 'Remarks Required', text: 'Please provide remarks for decline.', icon: 'warning' });
      return;
    }
    if (this.decisionStatus === 'REQUESTED_DOCS' && !this.requestedDocumentIds.length) {
      Swal.fire({ title: 'Select Documents', text: 'Please select at least one requested document.', icon: 'warning' });
      return;
    }
    Swal.fire({
      title: 'Save decision?',
      text: 'Are you sure you want to approve/decline this case request?',
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
          status: this.decisionStatus,
          decision_notes: this.decisionNotes || null,
          requested_document_index_ids:
            this.decisionStatus === 'REQUESTED_DOCS' ? this.requestedDocumentIds : [],
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

  setDecisionStatus(status: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS'): void {
    this.decisionStatus = status;
  }

  isRequestedDocument(docId: number): boolean {
    return this.requestedDocumentIds.includes(docId);
  }

  toggleRequestedDocument(docId: number, checked: boolean): void {
    if (checked) {
      if (!this.requestedDocumentIds.includes(docId)) {
        this.requestedDocumentIds = [...this.requestedDocumentIds, docId];
      }
      return;
    }
    this.requestedDocumentIds = this.requestedDocumentIds.filter((id) => id !== docId);
  }
}

