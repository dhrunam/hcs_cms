import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { debounceTime, distinctUntilChanged, Subject } from 'rxjs';
import { OfficeNoteSheetService, CaseItem } from '../services/office-note-sheet.service';

@Component({
  selector: 'app-office-note-sheet-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './list.html',
  styleUrl: './list.css',
})
export class OfficeNoteSheetList implements OnInit {
  cases: CaseItem[] = [];
  filteredCases: CaseItem[] = [];
  isLoading = false;
  searchQuery = '';
  private searchSubject = new Subject<string>();

  constructor(private officeNoteService: OfficeNoteSheetService) {}

  ngOnInit(): void {
    this.loadCases();
    this.searchSubject
      .pipe(debounceTime(300), distinctUntilChanged())
      .subscribe((query) => {
        this.filterCases(query);
      });
  }

  loadCases(): void {
    this.isLoading = true;
    this.officeNoteService.getCases({ page_size: 9999 }).subscribe({
      next: (response) => {
        this.cases = response.results || [];
        this.filteredCases = this.cases;
        this.isLoading = false;
      },
      error: () => {
        this.cases = [];
        this.filteredCases = [];
        this.isLoading = false;
      },
    });
  }

  onSearchChange(query: string): void {
    this.searchSubject.next(query);
  }

  private filterCases(query: string): void {
    if (!query.trim()) {
      this.filteredCases = this.cases;
      return;
    }
    const lowerQuery = query.toLowerCase();
    this.filteredCases = this.cases.filter(
      (c) =>
        c.case_number?.toLowerCase().includes(lowerQuery) ||
        c.petitioner_name?.toLowerCase().includes(lowerQuery),
    );
  }

  getStatusBadgeClass(status: string | null): string {
    if (!status) return 'bg-secondary-subtle';
    const s = status.toLowerCase();
    if (s.includes('accept') || s.includes('active')) return 'bg-success-subtle';
    if (s.includes('pending') || s.includes('draft')) return 'bg-warning-subtle';
    return 'bg-secondary-subtle';
  }

  trackByCaseId(index: number, item: CaseItem): number {
    return item.id;
  }
}