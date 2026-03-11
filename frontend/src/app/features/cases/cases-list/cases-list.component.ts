import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../../core/services/api.service';

interface Case {
  id: number;
  case_number: string;
  case_title: string;
  case_type: string;
  status: string;
  filed_date: string;
  [key: string]: unknown;
}

interface CasesResponse {
  results: Case[];
  count: number;
  next: string | null;
  previous: string | null;
}

@Component({
  selector: 'app-cases-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatTooltipModule,
  ],
  templateUrl: './cases-list.component.html',
  styleUrl: './cases-list.component.scss',
})
export class CasesListComponent implements OnInit, AfterViewInit {
  displayedColumns: string[] = [
    'case_number',
    'case_title',
    'case_type',
    'status',
    'filed_date',
    'actions',
  ];

  dataSource = new MatTableDataSource<Case>([]);
  isLoading = true;
  errorMessage = '';
  searchQuery = '';
  totalCount = 0;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadCases();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadCases(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.apiService.getCases().subscribe({
      next: (response) => {
        const data = response as CasesResponse;
        if (data && Array.isArray(data.results)) {
          this.dataSource.data = data.results;
          this.totalCount = data.count;
        } else if (Array.isArray(data)) {
          this.dataSource.data = data as unknown as Case[];
          this.totalCount = (data as unknown as Case[]).length;
        } else {
          this.dataSource.data = [];
        }
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load cases', err);
        this.errorMessage = 'Failed to load cases. Please try again.';
        this.isLoading = false;
      },
    });
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  getStatusColor(status: string): string {
    const map: Record<string, string> = {
      pending: 'accent',
      active: 'primary',
      disposed: '',
      closed: '',
    };
    return map[status?.toLowerCase()] ?? '';
  }

  refresh(): void {
    this.loadCases();
  }
}
