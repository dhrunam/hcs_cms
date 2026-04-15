import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { app_url } from '../../../environment';
import { PaginatedResponse } from '../../../shared/api/paginated.types';

const BASE = `${app_url}/api/v1/accounts/groups`;

export interface AdminRoleRow {
  id: number;
  name: string;
  description: string;
  permission_count: number;
}

@Injectable({ providedIn: 'root' })
export class RoleAdminService {
  private readonly http = inject(HttpClient);

  getRoles(params: {
    page: number;
    pageSize: number;
    search: string;
  }): Observable<PaginatedResponse<AdminRoleRow>> {
    let hp = new HttpParams()
      .set('page', String(params.page))
      .set('page_size', String(params.pageSize));
    const q = params.search.trim();
    if (q) {
      hp = hp.set('search', q);
    }
    return this.http.get<PaginatedResponse<AdminRoleRow>>(`${BASE}/`, { params: hp });
  }
}
