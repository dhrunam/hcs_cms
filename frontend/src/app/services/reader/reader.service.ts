import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { app_url } from '../../environment';

export type RegisteredCase = {
  efiling_id: number;
  case_number: string | null;
  e_filing_number?: string | null;
  bench: string | null;
  bench_key?: string | null;
  petitioner_name: string | null;
  respondent_name: string | null;
  cause_of_action: string | null;
  approval_status?: 'NOT_FORWARDED' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'REQUESTED_DOCS';
  approval_notes?: string[];
  approval_bench_key?: string | null;
  approval_forwarded_for_date?: string | null;
  approval_listing_date?: string | null;
  listing_summary?: string | null;
  requested_documents?: { document_index_id: number; document_part_name: string | null; document_type: string | null }[];
};

export type BenchConfiguration = {
  bench_key: string;
  label: string;
  bench_code: string | null;
  bench_name: string | null;
  judge_names: string[];
  judge_user_ids: number[];
  reader_user_ids: number[];
  is_accessible_to_reader: boolean;
  is_forward_target?: boolean;
};

export function resolveBenchConfiguration(
  benchConfigurations: BenchConfiguration[],
  benchValue: string | null | undefined,
): BenchConfiguration | undefined {
  const normalizedValue = String(benchValue ?? '').trim();
  if (!normalizedValue) {
    return undefined;
  }
  return benchConfigurations.find(
    (item) => item.bench_key === normalizedValue || item.bench_code === normalizedValue,
  );
}

@Injectable({
  providedIn: 'root',
})
export class ReaderService {
  constructor(private http: HttpClient) {}

  getBenchConfigurations(params?: { accessible_only?: boolean }): Observable<{ items: BenchConfiguration[] }> {
    const userGroup = sessionStorage.getItem('user_group');
    let url = `${app_url}/api/v1/reader/bench-configurations/`;
    const queryParts: string[] = [];
    if (params?.accessible_only) {
      queryParts.push('accessible_only=true');
    }
    if (userGroup) {
      queryParts.push(`reader_group=${encodeURIComponent(userGroup)}`);
    }
    if (queryParts.length > 0) {
      url += '?' + queryParts.join('&');
    }
    return this.http.get<{ items: BenchConfiguration[] }>(url);
  }

  getRegisteredCases(params?: { page_size?: number }): Observable<{ total: number; items: RegisteredCase[] }> {
    const userGroup = sessionStorage.getItem('user_group');
    let url = `${app_url}/api/v1/reader/registered-cases/`;
    const queryParts: string[] = [];
    if (params?.page_size != null) {
      queryParts.push(`page_size=${params.page_size}`);
    }
    if (userGroup) {
      queryParts.push(`reader_group=${userGroup}`);
    }
    if (queryParts.length > 0) {
      url += '?' + queryParts.join('&');
    }
    return this.http.get<any>(url);
  }

  assignBenches(assignments: { efiling_id: number; bench_key: string }[]): Observable<{ updated: number }> {
    return this.http.post<{ updated: number }>(`${app_url}/api/v1/reader/assign-bench/`, {
      assignments,
    });
  }

  forwardToCourtroom(payload: {
    forwarded_for_date: string;
    bench_key: string;
    listing_summary?: string | null;
    document_index_ids?: number[];
    efiling_ids: number[];
  }): Observable<{ updated: number }> {
    const userGroup = sessionStorage.getItem('user_group');
    let url = `${app_url}/api/v1/reader/forward/`;
    if (userGroup) {
      url += `?reader_group=${encodeURIComponent(userGroup)}`;
    }
    return this.http.post<{ updated: number }>(url, payload);
  }

  getApprovedCases(params: { bench_key: string; forwarded_for_date: string }): Observable<{ results: any[] }> {
    const userGroup = sessionStorage.getItem('user_group');
    let url = `${app_url}/api/v1/reader/approved-cases/?bench_key=${encodeURIComponent(params.bench_key)}&forwarded_for_date=${encodeURIComponent(params.forwarded_for_date)}`;
    if (userGroup) {
      url += `&reader_group=${userGroup}`;
    }
    return this.http.get<any>(url);
  }

  assignDate(payload: { efiling_ids: number[]; listing_date: string; forwarded_for_date: string; listing_remark?: string }): Observable<{ updated: number }> {
    const userGroup = sessionStorage.getItem('user_group');
    let url = `${app_url}/api/v1/reader/assign-date/`;
    if (userGroup) {
      url += `?reader_group=${encodeURIComponent(userGroup)}`;
    }
    return this.http.post<{ updated: number }>(url, payload);
  }

  resetBench(efilingId: number): Observable<any> {
    const userGroup = sessionStorage.getItem('user_group');
    let url = `${app_url}/api/v1/reader/reset-bench/`;
    if (userGroup) {
      url += `?reader_group=${userGroup}`;
    }
    return this.http.post<any>(url, { efiling_id: efilingId });
  }
}
