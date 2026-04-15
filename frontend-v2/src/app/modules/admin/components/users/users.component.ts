import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { PageEvent, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatTableModule } from '@angular/material/table';
import { Subject, Subscription, debounceTime, distinctUntilChanged } from 'rxjs';
import { AdminUserRow, UserAdminService } from '../../services/user-admin.service';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSlideToggleModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './users.component.html',
  styleUrl: './users.component.scss',
})
export class UsersComponent implements OnInit, OnDestroy {
  private readonly usersApi = inject(UserAdminService);
  private readonly searchTerms = new Subject<string>();
  private searchSub?: Subscription;

  /** Mat table column ids */
  readonly columnKeys: string[] = ['index', 'name', 'email', 'role', 'status'];

  readonly loading = signal(false);
  readonly errorMsg = signal<string | null>(null);
  readonly rows = signal<AdminUserRow[]>([]);
  readonly totalCount = signal(0);
  /** 1-based page for API */
  readonly page = signal(1);
  readonly pageSize = signal(10);
  readonly togglingId = signal<number | null>(null);

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
    this.usersApi
      .getUsers({
        page: this.page(),
        pageSize: this.pageSize(),
        search: this.search,
      })
      .subscribe({
        next: (res) => {
          this.rows.set(res.results);
          this.totalCount.set(res.count);
          this.loading.set(false);
        },
        error: (err: unknown) => {
          this.loading.set(false);
          this.errorMsg.set(this.formatHttpError(err));
        },
      });
  }

  onMatPage(e: PageEvent): void {
    this.page.set(e.pageIndex + 1);
    this.pageSize.set(e.pageSize);
    this.load();
  }

  /** Serial number: (page - 1) * pageSize + rowIndex + 1 */
  serialForRow(rowIndex: number): number {
    return (this.page() - 1) * this.pageSize() + rowIndex + 1;
  }

  roleLabel(row: AdminUserRow): string {
    const g = row.groups;
    if (!g?.length) {
      return '—';
    }
    return g.join(', ');
  }

  displayName(row: AdminUserRow): string {
    return row.full_name?.trim() || '—';
  }

  /** Maps API is_active to slide state (isActive semantics in UI). */
  isUserActive(row: AdminUserRow): boolean {
    return row.is_active;
  }

  onToggle(row: AdminUserRow, checked: boolean): void {
    if (row.is_active === checked) {
      return;
    }
    const prev = row.is_active;
    this.rows.update((list) =>
      list.map((r) => (r.id === row.id ? { ...r, is_active: checked } : r)),
    );
    this.togglingId.set(row.id);
    this.usersApi.toggleActive(row.id, checked).subscribe({
      next: (updated) => {
        this.rows.update((list) => list.map((r) => (r.id === updated.id ? updated : r)));
        this.togglingId.set(null);
      },
      error: (err: unknown) => {
        this.rows.update((list) =>
          list.map((r) => (r.id === row.id ? { ...r, is_active: prev } : r)),
        );
        this.togglingId.set(null);
        this.errorMsg.set(this.formatHttpError(err));
      },
    });
  }

  private formatHttpError(err: unknown): string {
    if (err && typeof err === 'object' && 'error' in err) {
      const e = err as { error?: { detail?: unknown } };
      const d = e.error?.detail;
      if (typeof d === 'string') {
        return d;
      }
    }
    return 'Could not complete the request. Check your connection and permissions.';
  }
}
