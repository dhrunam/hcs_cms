import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { app_url } from '../../../environment';
import { PaginatedResponse } from '../../../shared/api/paginated.types';

const BASE = `${app_url}/api/v1/accounts/permissions`;

export interface AdminPermissionRow {
  id: number;
  name: string;
  codename: string;
  description: string;
}

@Injectable({ providedIn: 'root' })
export class PermissionAdminService {
  private readonly http = inject(HttpClient);

  getPermissions(params: {
    page: number;
    pageSize: number;
    search: string;
  }): Observable<PaginatedResponse<AdminPermissionRow>> {
    let hp = new HttpParams()
      .set('page', String(params.page))
      .set('page_size', String(params.pageSize));
    const q = params.search.trim();
    if (q) {
      hp = hp.set('search', q);
    }
    return this.http.get<PaginatedResponse<AdminPermissionRow>>(`${BASE}/`, { params: hp });
  }
}
