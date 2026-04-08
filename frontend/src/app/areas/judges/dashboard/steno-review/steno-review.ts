import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';

import { CourtroomService } from '../../../../services/judge/courtroom.service';

@Component({
  selector: 'app-judge-steno-review',
  imports: [CommonModule, FormsModule],
  templateUrl: './steno-review.html',
  styleUrl: './steno-review.css',
})
export class JudgeStenoReviewPage {
  items: any[] = [];
  isLoading = false;
  notes: Record<number, string> = {};
  annotationText: Record<number, string> = {};

  constructor(private courtroomService: CourtroomService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading = true;
    this.courtroomService.getStenoWorkflows().subscribe({
      next: (resp) => {
        this.items = resp?.items ?? [];
        this.isLoading = false;
      },
      error: () => {
        this.items = [];
        this.isLoading = false;
      },
    });
  }

  addAnnotation(item: any): void {
    const note = (this.annotationText[item.workflow_id] || '').trim();
    if (!note) return;
    this.courtroomService.addStenoWorkflowAnnotation({ workflow_id: item.workflow_id, note_text: note }).subscribe({
      next: () => {
        this.annotationText[item.workflow_id] = '';
        Swal.fire({ title: 'Note added', icon: 'success', timer: 900, showConfirmButton: false });
      },
      error: () => Swal.fire('Error', 'Failed to save note.', 'error'),
    });
  }

  decide(item: any, decision: 'APPROVED' | 'REJECTED'): void {
    this.courtroomService
      .decideStenoWorkflow({
        workflow_id: item.workflow_id,
        judge_approval_status: decision,
        judge_approval_notes: this.notes[item.workflow_id] || null,
      })
      .subscribe({
        next: () => {
          Swal.fire({ title: decision === 'APPROVED' ? 'Approved' : 'Sent back', icon: 'success', timer: 1000, showConfirmButton: false });
          this.load();
        },
        error: () => Swal.fire('Error', 'Failed to save decision.', 'error'),
      });
  }
}

