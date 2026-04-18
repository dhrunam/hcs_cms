import { CommonModule } from '@angular/common';
import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import { OfficeNoteSheetService, OfficeNote } from '../services/office-note-sheet.service';

@Component({
  selector: 'app-office-note-editor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './note-editor.html',
  styleUrl: './note-editor.css',
})
export class OfficeNoteEditor implements OnInit, OnDestroy {
  @Input() caseId: number | null = null;
  @Input() showHeader = true;
  notes: OfficeNote[] = [];
  newNoteContent = '';
  isLoading = false;
  isSaving = false;
  private destroy$ = new Subject<void>();

  constructor(
    private router: Router,
    private officeNoteService: OfficeNoteSheetService,
  ) {}

  ngOnInit(): void {
    if (!this.caseId) {
      return;
    }
    this.loadNotes();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadNotes(): void {
    if (!this.caseId) return;
    this.isLoading = true;
    this.officeNoteService.getNotesByCaseId(this.caseId).subscribe({
      next: (notes) => {
        this.notes = notes;
        this.isLoading = false;
      },
      error: () => {
        this.notes = [];
        this.isLoading = false;
      },
    });
  }

  saveNote(): void {
    if (!this.isValidNote() || !this.caseId) return;
    this.isSaving = true;
    const payload = { case_id: this.caseId, note_content: this.newNoteContent.trim() };
    this.officeNoteService.createNote(payload).subscribe({
      next: (note) => {
        this.notes.unshift(note);
        this.newNoteContent = '';
        this.isSaving = false;
      },
      error: () => {
        this.isSaving = false;
      },
    });
  }

  get wordCount(): number {
    if (!this.newNoteContent.trim()) return 0;
    return this.newNoteContent.trim().split(/\s+/).length;
  }

  isValidNote(): boolean {
    const count = this.wordCount;
    return count > 0 && count <= 200;
  }

  goBack(): void {
    this.navigateBack();
  }

  private getBasePath(): string {
    const url = this.router.url;
    const segments = url.split('/');
    if (segments.length >= 2) {
      return '/' + segments[1] + '/' + segments[2];
    }
    return '/reader/dashboard';
  }

  private navigateBack(): void {
    this.router.navigate([this.getBasePath() + '/office-note-sheet']);
  }

  trackByNoteId(index: number, note: OfficeNote): number {
    return note.id;
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }
}