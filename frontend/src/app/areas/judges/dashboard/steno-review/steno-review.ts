import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';

import { CourtroomService } from '../../../../services/judge/courtroom.service';
import { PdfAnnotatorComponent } from '../courtroom/pdf-annotator.component';

/** Store normalized 0–1 coords as 0–1000 in the API (3 decimal places). */
function toApiCoord(v: number): number {
  return Math.round(Math.min(1, Math.max(0, v)) * 1000 * 1000) / 1000;
}

@Component({
  selector: 'app-judge-steno-review',
  imports: [CommonModule, FormsModule, PdfAnnotatorComponent],
  templateUrl: './steno-review.html',
  styleUrl: './steno-review.css',
})
export class JudgeStenoReviewPage {
  items: any[] = [];
  isLoading = false;
  statusFilter:
    | 'ALL'
    | 'SENT_FOR_JUDGE_APPROVAL'
    | 'CHANGES_REQUESTED'
    | 'JUDGE_APPROVED'
    | 'SIGNED_AND_PUBLISHED' = 'SENT_FOR_JUDGE_APPROVAL';
  selectedWorkflowId: number | null = null;
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
        const firstVisible = this.filteredItems[0];
        this.selectedWorkflowId = firstVisible ? Number(firstVisible.workflow_id) : null;
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

  canAnnotate(item: any): boolean {
    const status = item?.workflow_status;
    return status === 'SENT_FOR_JUDGE_APPROVAL' || status === 'CHANGES_REQUESTED';
  }

  decisionHint(item: any): string {
    if (this.canDecide(item)) return 'Ready for judge decision.';
    const status = this.statusLabel(item?.workflow_status);
    return `Decision unavailable in current status: ${status}.`;
  }

  isSelected(item: any): boolean {
    return Number(this.selectedWorkflowId) === Number(item?.workflow_id);
  }

  /** Hydrate PDF annotator from saved JudgeDraftAnnotation rows. */
  annotationPayloadFor(item: any): { pages: any[] } {
    const list = item?.judge_annotations;
    if (!Array.isArray(list) || !list.length) {
      return { pages: [] };
    }
    const byPage = new Map<number, { pageIndex: number; paths: any[]; notes: any[] }>();
    const getPage = (idx: number) => {
      if (!byPage.has(idx)) {
        byPage.set(idx, { pageIndex: idx, paths: [], notes: [] });
      }
      return byPage.get(idx)!;
    };
    const num = (v: string | null | undefined): number | null => {
      if (v == null || v === '') return null;
      const n = Number(v);
      return Number.isFinite(n) ? n : null;
    };

    for (const a of list) {
      const xS = num(a.x);
      const yS = num(a.y);
      const wS = num(a.width);
      const hS = num(a.height);
      const hasPos =
        a.page_number != null ||
        xS != null ||
        yS != null ||
        wS != null ||
        hS != null;
      if (!hasPos) {
        continue;
      }

      const pi = Math.max(0, (a.page_number != null ? Number(a.page_number) : 1) - 1);
      const pg = getPage(pi);
      const xN = xS != null ? xS / 1000 : 0.08;
      const yN = yS != null ? yS / 1000 : 0.08;

      if (a.annotation_type === 'HIGHLIGHT' && wS != null && hS != null && wS > 0 && hS > 0) {
        const w = wS / 1000;
        const h = hS / 1000;
        const x = xN;
        const y = yN;
        pg.paths.push({
          type: 'highlighter',
          color: 'rgba(255, 255, 0, 0.4)',
          width: 16,
          points: [
            { x, y },
            { x: x + w, y },
            { x: x + w, y: y + h },
            { x, y: y + h },
            { x, y },
          ],
        });
      } else if (a.annotation_type === 'FORMAT' && wS != null && hS != null && wS > 0 && hS > 0) {
        const w = wS / 1000;
        const h = hS / 1000;
        const x = xN;
        const y = yN;
        pg.paths.push({
          type: 'pen',
          color: '#cc0000',
          width: 2,
          points: [
            { x, y },
            { x: x + w, y: y + h },
          ],
        });
      } else {
        pg.notes.push({
          x: xN,
          y: yN,
          text: String(a.note_text || ''),
        });
      }
    }
    return { pages: Array.from(byPage.values()) };
  }

  onAnnotatorSave(item: any, payload: { pages?: any[] }): void {
    const wid = item.workflow_id;
    const annotations: {
      page_number?: number | null;
      note_text: string;
      annotation_type: 'COMMENT' | 'HIGHLIGHT' | 'TEXT_REPLACE' | 'FORMAT';
      x?: number | null;
      y?: number | null;
      width?: number | null;
      height?: number | null;
    }[] = [];

    for (const page of payload.pages || []) {
      const pageNum = (page.pageIndex ?? 0) + 1;

      for (const note of page.notes || []) {
        const t = String(note.text || '').trim();
        if (!t) continue;
        annotations.push({
          note_text: t,
          annotation_type: 'COMMENT',
          page_number: pageNum,
          x: toApiCoord(Number(note.x)),
          y: toApiCoord(Number(note.y)),
        });
      }

      for (const path of page.paths || []) {
        const pts: { x: number; y: number }[] = path.points || [];
        if (pts.length < 2) continue;
        const xs = pts.map((p) => p.x);
        const ys = pts.map((p) => p.y);
        const minx = Math.min(...xs);
        const maxx = Math.max(...xs);
        const miny = Math.min(...ys);
        const maxy = Math.max(...ys);
        const w = Math.max(0.001, maxx - minx);
        const h = Math.max(0.001, maxy - miny);
        const isHi = path.type === 'highlighter';
        annotations.push({
          note_text: isHi ? 'Highlight' : 'Correction mark',
          annotation_type: isHi ? 'HIGHLIGHT' : 'FORMAT',
          page_number: pageNum,
          x: toApiCoord(minx),
          y: toApiCoord(miny),
          width: toApiCoord(w),
          height: toApiCoord(h),
        });
      }
    }

    this.courtroomService.saveStenoWorkflowAnnotationsSnapshot({ workflow_id: wid, annotations }).subscribe({
      next: (r) => {
        const msg =
          r.saved === 0
            ? 'PDF mark-up cleared (text-only notes are unchanged).'
            : `${r.saved} annotation(s) recorded.`;
        void Swal.fire({
          title: 'Saved',
          text: msg,
          icon: 'success',
          timer: 1400,
          showConfirmButton: false,
        });
        this.load();
      },
      error: () => {
        void Swal.fire('Error', 'Failed to save annotations.', 'error');
      },
    });
  }

  addAnnotation(item: any): void {
    const note = (this.annotationText[item.workflow_id] || '').trim();
    if (!note) return;
    this.courtroomService.addStenoWorkflowAnnotation({ workflow_id: item.workflow_id, note_text: note }).subscribe({
      next: () => {
        this.annotationText[item.workflow_id] = '';
        void Swal.fire({ title: 'Note added', icon: 'success', timer: 900, showConfirmButton: false });
        this.load();
      },
      error: () => void Swal.fire('Error', 'Failed to save note.', 'error'),
    });
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
