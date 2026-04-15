import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { PageEvent, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { Subject, Subscription, debounceTime, distinctUntilChanged } from 'rxjs';
import { AdminRoleRow, RoleAdminService } from '../../services/role-admin.service';

@Component({
  selector: 'app-admin-roles',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './roles.component.html',
  styleUrl: './roles.component.scss',
})
export class RolesComponent implements OnInit, OnDestroy {
  private readonly api = inject(RoleAdminService);
  private readonly searchTerms = new Subject<string>();
  private searchSub?: Subscription;

  readonly columnKeys: string[] = ['index', 'name', 'description', 'permission_count'];

  readonly loading = signal(false);
  readonly errorMsg = signal<string | null>(null);
  readonly rows = signal<AdminRoleRow[]>([]);
  readonly totalCount = signal(0);
  readonly page = signal(1);
  readonly pageSize = signal(10);
  search = '';

  ngOnInit(): void {
    this.searchSub = this.searchTerms
      .pipe(debounceTime(300), distinctUntilChanged())
      .subscribe(() => {
        this.page.set(1);
        this.load();
      });
    this.load();
  }

  ngOnDestroy(): void {
    this.searchSub?.unsubscribe();
  }

  onSearchInput(value: string): void {
    this.search = value;
    this.searchTerms.next(value);
  }

  load(): void {
    this.loading.set(true);
    this.errorMsg.set(null);
    this.api.getRoles({ page: this.page(), pageSize: this.pageSize(), search: this.search }).subscribe({
      next: (res) => {
        this.rows.set(res.results);
        this.totalCount.set(res.count);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.errorMsg.set('Could not load roles.');
      },
    });
  }

  onMatPage(e: PageEvent): void {
    this.page.set(e.pageIndex + 1);
    this.pageSize.set(e.pageSize);
    this.load();
  }

  serialForRow(rowIndex: number): number {
    return (this.page() - 1) * this.pageSize() + rowIndex + 1;
  }
}
