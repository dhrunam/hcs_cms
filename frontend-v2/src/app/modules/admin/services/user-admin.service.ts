import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { app_url } from '../../../environment';
import { PaginatedResponse } from '../../../shared/api/paginated.types';

const BASE = `${app_url}/api/v1/accounts/users`;

export interface AdminUserRow {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  groups: string[];
  is_active: boolean;
}

@Injectable({ providedIn: 'root' })
export class UserAdminService {
  private readonly http = inject(HttpClient);

  getUsers(params: {
    page: number;
    pageSize: number;
    search: string;
  }): Observable<PaginatedResponse<AdminUserRow>> {
    let hp = new HttpParams()
      .set('page', String(params.page))
      .set('page_size', String(params.pageSize));
    const q = params.search.trim();
    if (q) {
      hp = hp.set('search', q);
    }
    return this.http.get<PaginatedResponse<AdminUserRow>>(`${BASE}/`, { params: hp });
  }

  /** PATCH /users/{id}/active/ — body uses camelCase isActive per API contract. */
  toggleActive(userId: number, isActive: boolean): Observable<AdminUserRow> {
    return this.http.patch<AdminUserRow>(`${BASE}/${userId}/active/`, { isActive });
  }
}
