import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../../auth.service';
import { app_url } from '../../environment';

export type ReaderOverallStatus =
  | 'not_forwarded'
  | 'in_review'
  | 'ready_for_listing'
  | 'rejected'
  | 'requested_docs';

export type RegisteredCase = {
  efiling_id: number;
  case_number: string | null;
  e_filing_number?: string | null;
  bench: string | null;
  bench_key?: string | null;
  petitioner_name: string | null;
  respondent_name: string | null;
  petitioner_vs_respondent?: string | null;
  cause_of_action: string | null;
  approval_status?: 'NOT_FORWARDED' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'REQUESTED_DOCS';
  /** Combined bench state; prefer for labels over raw approval_status on division benches. */
  overall_status?: ReaderOverallStatus;
  /** Whether this reader created a forward for their slot. */
  my_forward_status?: 'forwarded' | 'not_forwarded';
  /** True if any forward exists for this bench/date (may be another reader). */
  bench_has_forward?: boolean;
  all_judges_reviewed?: boolean;
  judge_status_by_role?: Record<string, string>;
  approval_notes?: string[];
  approval_bench_key?: string | null;
  approval_forwarded_for_date?: string | null;
  approval_listing_date?: string | null;
  listing_summary?: string | null;
  can_assign_listing_date?: boolean;
  requested_documents?: { document_index_id: number; document_part_name: string | null; document_type: string | null }[];
};

export type BenchConfiguration = {
  bench_key: string;
  label: string;
  bench_code: string | null;
  bench_name: string | null;
  judge_names: string[];
  /** Names for slots this reader is mapped to (division benches may omit other judges). */
  mapped_judge_names?: string[];
  judge_user_ids: number[];
  reader_user_ids: number[];
  is_accessible_to_reader: boolean;
  is_forward_target?: boolean;
};

export type ReaderDailyProceedingCase = {
  efiling_id: number;
  case_number: string | null;
  e_filing_number?: string | null;
  petitioner_name: string | null;
  bench: string | null;
  bench_key?: string | null;
  last_hearing_date?: string | null;
  last_next_listing_date?: string | null;
  latest_proceedings_text?: string | null;
  listing_sync_status?: string | null;
  steno_workflow_status?: string | null;
  can_assign_listing_date: boolean;
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
  constructor(
    private http: HttpClient,
    private auth: AuthService,
  ) {}

  /**
   * Picks a stable `reader_group` query value for reader APIs (generic READER role).
   */
  private readerGroupForQuery(): string | null {
    const groups = this.auth.getUserGroups();
    const set = new Set(groups.map((g) => g.trim()));
    if (set.has('READER')) {
      return 'READER';
    }
    return sessionStorage.getItem('user_group')?.trim() || null;
  }

  getBenchConfigurations(params?: { accessible_only?: boolean }): Observable<{ items: BenchConfiguration[] }> {
    const readerGroup = this.readerGroupForQuery();
    let url = `${app_url}/api/v1/reader/bench-configurations/`;
    const queryParts: string[] = [];
    if (params?.accessible_only) {
      queryParts.push('accessible_only=true');
    }
    if (readerGroup) {
      queryParts.push(`reader_group=${encodeURIComponent(readerGroup)}`);
    }
    if (queryParts.length > 0) {
      url += '?' + queryParts.join('&');
    }
    return this.http.get<{ items: BenchConfiguration[] }>(url);
  }

  getRegisteredCases(params?: { page_size?: number }): Observable<{ total: number; items: RegisteredCase[] }> {
    const readerGroup = this.readerGroupForQuery();
    let url = `${app_url}/api/v1/reader/registered-cases/`;
    const queryParts: string[] = [];
    if (params?.page_size != null) {
      queryParts.push(`page_size=${params.page_size}`);
    }
    if (readerGroup) {
      queryParts.push(`reader_group=${encodeURIComponent(readerGroup)}`);
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
    const readerGroup = this.readerGroupForQuery();
    let url = `${app_url}/api/v1/reader/forward/`;
    if (readerGroup) {
      url += `?reader_group=${encodeURIComponent(readerGroup)}`;
    }
    return this.http.post<{ updated: number }>(url, payload);
  }

  getApprovedCases(params: { bench_key: string; forwarded_for_date: string }): Observable<{ results: any[] }> {
    const readerGroup = this.readerGroupForQuery();
    let url = `${app_url}/api/v1/reader/approved-cases/?bench_key=${encodeURIComponent(params.bench_key)}&forwarded_for_date=${encodeURIComponent(params.forwarded_for_date)}`;
    if (readerGroup) {
      url += `&reader_group=${encodeURIComponent(readerGroup)}`;
    }
    return this.http.get<any>(url);
  }

  assignDate(payload: { efiling_ids: number[]; listing_date: string; forwarded_for_date: string; listing_remark?: string }): Observable<{ updated: number }> {
    const readerGroup = this.readerGroupForQuery();
    let url = `${app_url}/api/v1/reader/assign-date/`;
    if (readerGroup) {
      url += `?reader_group=${encodeURIComponent(readerGroup)}`;
    }
    return this.http.post<{ updated: number }>(url, payload);
  }

  resetBench(efilingId: number): Observable<any> {
    const readerGroup = this.readerGroupForQuery();
    let url = `${app_url}/api/v1/reader/reset-bench/`;
    if (readerGroup) {
      url += `?reader_group=${encodeURIComponent(readerGroup)}`;
    }
    return this.http.post<any>(url, { efiling_id: efilingId });
  }

  getDailyProceedings(params?: {
    page_size?: number;
    cause_list_date?: string;
  }): Observable<{ total: number; items: ReaderDailyProceedingCase[] }> {
    const readerGroup = this.readerGroupForQuery();
    let url = `${app_url}/api/v1/reader/daily-proceedings/`;
    const queryParts: string[] = [];
    if (params?.page_size != null) {
      queryParts.push(`page_size=${params.page_size}`);
    }
    if (params?.cause_list_date) {
      queryParts.push(`cause_list_date=${encodeURIComponent(params.cause_list_date)}`);
    }
    if (readerGroup) {
      queryParts.push(`reader_group=${encodeURIComponent(readerGroup)}`);
    }
    if (queryParts.length > 0) {
      url += '?' + queryParts.join('&');
    }
    return this.http.get<{ total: number; items: ReaderDailyProceedingCase[] }>(url);
  }

  submitDailyProceeding(payload: {
    efiling_id: number;
    hearing_date: string;
    next_listing_date: string;
    proceedings_text: string;
    reader_remark?: string | null;
    steno_remark?: string | null;
    listing_remark?: string | null;
    document_type?: 'ORDER' | 'JUDGMENT';
  }): Observable<any> {
    const readerGroup = this.readerGroupForQuery();
    let url = `${app_url}/api/v1/reader/daily-proceedings/submit/`;
    if (readerGroup) {
      url += `?reader_group=${encodeURIComponent(readerGroup)}`;
    }
    return this.http.post<any>(url, payload);
  }

  getStenoQueue(): Observable<{ items: any[] }> {
    return this.http.get<{ items: any[] }>(`${app_url}/api/v1/reader/steno/queue/`);
  }

  uploadStenoDraft(payload: {
    workflow_id: number;
    draft_document_index_id: number;
  }): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/reader/steno/upload-draft/`, payload);
  }

  /** Multipart PDF upload; creates EfilingDocumentsIndex on the case. */
  uploadStenoDraftFile(workflowId: number, file: File): Observable<{
    workflow_status: string;
    draft_document_index_id: number;
    draft_preview_url?: string | null;
  }> {
    const fd = new FormData();
    fd.append('workflow_id', String(workflowId));
    fd.append('file', file, file.name);
    return this.http.post<any>(`${app_url}/api/v1/reader/steno/upload-draft-file/`, fd);
  }

  submitStenoToJudge(payload: { workflow_id: number }): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/reader/steno/submit-judge/`, payload);
  }

  uploadSignedAndPublish(
    workflowId: number,
    file: File,
    signature?: {
      signature_provider?: string | null;
      certificate_serial?: string | null;
      signer_name?: string | null;
      signature_reason?: string | null;
      signature_txn_id?: string | null;
    },
  ): Observable<{
    workflow_status: string;
    signed_document_index_id: number;
    signed_preview_url?: string | null;
    digitally_signed_at?: string | null;
    published_at?: string | null;
  }> {
    const fd = new FormData();
    fd.append('workflow_id', String(workflowId));
    fd.append('file', file, file.name);
    if (signature?.signature_provider) fd.append('signature_provider', signature.signature_provider);
    if (signature?.certificate_serial) fd.append('certificate_serial', signature.certificate_serial);
    if (signature?.signer_name) fd.append('signer_name', signature.signer_name);
    if (signature?.signature_reason) fd.append('signature_reason', signature.signature_reason);
    if (signature?.signature_txn_id) fd.append('signature_txn_id', signature.signature_txn_id);
    return this.http.post<any>(`${app_url}/api/v1/reader/steno/upload-signed-publish/`, fd);
  }
}
