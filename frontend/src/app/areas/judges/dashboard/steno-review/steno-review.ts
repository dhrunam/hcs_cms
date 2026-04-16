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
  isDistractionFree = false;
  statusFilter:
    | 'ALL'
    | 'SENT_FOR_JUDGE_APPROVAL'
    | 'CHANGES_REQUESTED'
    | 'JUDGE_APPROVED'
    | 'SIGNED_AND_PUBLISHED' = 'SENT_FOR_JUDGE_APPROVAL';
  selectedWorkflowId: number | null = null;
  notes: Record<number, string> = {};

  constructor(private courtroomService: CourtroomService) {}

  ngOnInit(): void {
    this.load();
  }

  load(preserveSelection: boolean = true): void {
    this.isLoading = true;
    const previousSelectedWorkflowId = preserveSelection
      ? this.selectedWorkflowId
      : null;
    this.courtroomService.getStenoWorkflows().subscribe({
      next: (resp) => {
        this.items = resp?.items ?? [];
        const firstVisible = this.filteredItems[0];
        const keepPrevious =
          previousSelectedWorkflowId != null &&
          this.filteredItems.some(
            (item) =>
              Number(item.workflow_id) === Number(previousSelectedWorkflowId),
          );
        this.selectedWorkflowId = keepPrevious
          ? Number(previousSelectedWorkflowId)
          : firstVisible
            ? Number(firstVisible.workflow_id)
            : null;
        this.isLoading = false;
      },
      error: () => {
        this.items = [];
        this.isLoading = false;
      },
    });
  }

  get totalCount(): number {
    return this.items.length;
  }

  get pendingCount(): number {
    return this.items.filter((x) => x?.workflow_status === 'SENT_FOR_JUDGE_APPROVAL').length;
  }

  get changesRequestedCount(): number {
    return this.items.filter((x) => x?.workflow_status === 'CHANGES_REQUESTED').length;
  }

  get approvedCount(): number {
    return this.items.filter((x) => x?.workflow_status === 'JUDGE_APPROVED').length;
  }

  get publishedCount(): number {
    return this.items.filter((x) => x?.workflow_status === 'SIGNED_AND_PUBLISHED').length;
  }

  groupedItems(status: string): any[] {
    return this.items.filter((x) => x?.workflow_status === status);
  }

  get filteredItems(): any[] {
    if (this.statusFilter === 'ALL') {
      return this.items;
    }
    return this.groupedItems(this.statusFilter);
  }

  get selectedItem(): any | null {
    if (this.selectedWorkflowId == null) return null;
    return this.items.find((item) => Number(item.workflow_id) === Number(this.selectedWorkflowId)) || null;
  }

  setFilter(
    filter:
      | 'ALL'
      | 'SENT_FOR_JUDGE_APPROVAL'
      | 'CHANGES_REQUESTED'
      | 'JUDGE_APPROVED'
      | 'SIGNED_AND_PUBLISHED',
  ): void {
    this.statusFilter = filter;
    const selected = this.selectedItem;
    if (selected && this.filteredItems.some((item) => item.workflow_id === selected.workflow_id)) {
      return;
    }
    this.selectedWorkflowId = this.filteredItems[0]?.workflow_id ?? null;
  }

  selectItem(item: any): void {
    this.selectedWorkflowId = Number(item.workflow_id);
  }

  toggleDistractionFree(): void {
    this.isDistractionFree = !this.isDistractionFree;
  }

  draftOptionLabel(draft: any): string {
    const caseNumber = draft?.case_number || '-';
    const parties = draft?.petitioner_vs_respondent || '-';
    const workflowId = draft?.workflow_id ?? '-';
    return `${caseNumber} | ${parties} | WF #${workflowId}`;
  }

  statusLabel(status: string | null | undefined): string {
    return String(status || 'PENDING').replaceAll('_', ' ');
  }

  statusBadgeClass(status: string | null | undefined): string {
    const value = String(status || '');
    if (value === 'SENT_FOR_JUDGE_APPROVAL') return 'badge-pending';
    if (value === 'CHANGES_REQUESTED') return 'badge-warning';
    if (value === 'JUDGE_APPROVED') return 'badge-success';
    if (value === 'SIGNED_AND_PUBLISHED') return 'badge-muted';
    return 'badge-muted';
  }

  canDecide(item: any): boolean {
    return item?.workflow_status === 'SENT_FOR_JUDGE_APPROVAL';
  }

  decisionHint(item: any): string {
    if (this.canDecide(item)) return 'Ready for judge decision.';
    const status = this.statusLabel(item?.workflow_status);
    return `Decision unavailable in current status: ${status}.`;
  }

  isSelected(item: any): boolean {
    return Number(this.selectedWorkflowId) === Number(item?.workflow_id);
  }

  pdfUrlFor(item: any): string {
    const raw = item?.draft_preview_url;
    if (!raw) return '';
    return this.courtroomService.resolveDocumentUrl(raw);
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
          void Swal.fire({
            title: decision === 'APPROVED' ? 'Approved' : 'Sent back',
            icon: 'success',
            timer: 1000,
            showConfirmButton: false,
          });
          this.load();
        },
        error: () => void Swal.fire('Error', 'Failed to save decision.', 'error'),
      });
  }
}
