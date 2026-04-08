import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';

import { ReaderService } from '../../../../services/reader/reader.service';

@Component({
  selector: 'app-steno-home',
  imports: [CommonModule, FormsModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class StenoHomePage {
  isLoading = false;
  items: any[] = [];
  draftDocIds: Record<number, number> = {};

  constructor(private readerService: ReaderService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading = true;
    this.readerService.getStenoQueue().subscribe({
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

  uploadDraft(item: any): void {
    const docId = Number(this.draftDocIds[item.workflow_id] || 0);
    if (!docId) return;
    this.readerService.uploadStenoDraft({ workflow_id: item.workflow_id, draft_document_index_id: docId }).subscribe({
      next: () => {
        Swal.fire({ title: 'Draft linked', icon: 'success', timer: 900, showConfirmButton: false });
        this.load();
      },
      error: () => Swal.fire('Error', 'Failed to upload draft reference.', 'error'),
    });
  }

  submitToJudge(item: any): void {
    this.readerService.submitStenoToJudge({ workflow_id: item.workflow_id }).subscribe({
      next: () => {
        Swal.fire({ title: 'Sent', text: 'Sent to judge for approval.', icon: 'success', timer: 1000, showConfirmButton: false });
        this.load();
      },
      error: () => Swal.fire('Error', 'Failed to send to judge.', 'error'),
    });
  }
}

