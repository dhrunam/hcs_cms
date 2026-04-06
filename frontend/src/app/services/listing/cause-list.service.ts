import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { app_url } from '../../environment';

export type DraftPreviewItem = {
  efiling_id: number;
  case_number: string | null;
  e_filing_number?: string | null;
  petitioner_name?: string | null;
  petitioner_vs_respondent?: string | null;
  included: boolean;
  serial_no: number | null;
  petitioner_advocate?: string | null;
  respondent_advocate?: string | null;
  available_ias?: Array<{ ia_number: string; ia_text: string }>;
  selected_ias?: Array<{ ia_number: string; ia_text: string }>;
  judge_listing_date?: string | null;
  reader_listing_remark?: string | null;
};

export type DraftPreviewResponse = {
  cause_list_id: number | null;
  cause_list_date: string;
  bench_key: string;
  items: DraftPreviewItem[];
};

export type RegisteredCase = {
  efiling_id: number;
  case_number: string | null;
  e_filing_number?: string | null;
  bench: string | null;
  petitioner_name: string | null;
  respondent_name: string | null;
  petitioner_vs_respondent?: string | null;
  cause_of_action: string | null;
  date_of_cause_of_action: string | null;
  dispute_state: string | null;
  dispute_district: string | null;
  dispute_taluka: string | null;
  scrutiny_remarks: string | null;
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
};

@Injectable({
  providedIn: 'root',
})
export class CauseListService {
  constructor(private http: HttpClient) {}

  getBenchConfigurations(): Observable<{ items: BenchConfiguration[] }> {
    return this.http.get<{ items: BenchConfiguration[] }>(
      `${app_url}/api/v1/reader/bench-configurations/`,
    );
  }

  getDraftPreview(
    cause_list_date: string,
    bench_key: string,
    approvedOnly: boolean = true,
  ): Observable<DraftPreviewResponse> {
    const url = `${app_url}/api/v1/listing/cause-lists/draft/preview/?cause_list_date=${encodeURIComponent(
      cause_list_date,
    )}&bench_key=${encodeURIComponent(bench_key)}&approved_only=${approvedOnly ? "true" : "false"}`;
    return this.http.get<DraftPreviewResponse>(url);
  }

  getDraftPdfUrl(cause_list_date: string, bench_key: string): string {
    return `${app_url}/api/v1/listing/cause-lists/draft/pdf/?cause_list_date=${encodeURIComponent(
      cause_list_date,
    )}&bench_key=${encodeURIComponent(bench_key)}`;
  }

  saveDraft(payload: {
    cause_list_date: string;
    bench_key: string;
    entries: {
      efiling_id: number;
      serial_no: number | null;
      included: boolean;
      petitioner_advocate?: string | null;
      respondent_advocate?: string | null;
      selected_ias?: Array<{ ia_number: string; ia_text: string }>;
    }[];
  }): Observable<{ cause_list_id: number; status: string }> {
    return this.http.post<{ cause_list_id: number; status: string }>(
      `${app_url}/api/v1/listing/cause-lists/draft/save/`,
      payload,
    );
  }

  publishCauseList(cause_list_id: number): Observable<{ id: number; status: string; pdf_url: string | null }> {
    return this.http.post<{ id: number; status: string; pdf_url: string | null }>(
      `${app_url}/api/v1/listing/cause-lists/${cause_list_id}/publish/`,
      {},
    );
  }

  publishCauseListDirect(payload: {
    cause_list_date: string;
    bench_key: string;
    entries: {
      efiling_id: number;
      serial_no: number | null;
      included: boolean;
      petitioner_advocate?: string | null;
      respondent_advocate?: string | null;
      selected_ias?: Array<{ ia_number: string; ia_text: string }>;
    }[];
  }): Observable<{ id: number; status: string; pdf_url: string | null }> {
    return this.http.post<{ id: number; status: string; pdf_url: string | null }>(
      `${app_url}/api/v1/listing/cause-lists/publish/`,
      payload,
    );
  }

  forwardToCourtroom(payload: {
    forwarded_for_date: string;
    bench_key: string;
    listing_summary?: string | null;
    document_index_ids?: number[];
    efiling_ids: number[];
  }): Observable<{ updated: number; skipped?: number; errors?: { efiling_id: number; detail: string }[] }> {
    return this.http.post<{ updated: number; skipped?: number; errors?: { efiling_id: number; detail: string }[] }>(
      `${app_url}/api/v1/judge/courtroom/forward/`,
      payload,
    );
  }

  getPublishedCauseLists(cause_list_date: string): Observable<{
    items: { id: number; bench_key: string; included_count?: number; pdf_url: string | null }[];
  }> {
    const url = `${app_url}/api/v1/listing/cause-lists/published/?cause_list_date=${encodeURIComponent(
      cause_list_date,
    )}`;
    return this.http.get<any>(url);
  }

  getLatestPublishedCauseLists(): Observable<{
    found: boolean;
    cause_list_date: string | null;
    items: { id: number; bench_key: string; pdf_url: string | null }[];
  }> {
    return this.http.get<any>(`${app_url}/api/v1/listing/cause-lists/published/latest/`);
  }

  lookupLatestPublishedForCases(case_numbers: string[]): Observable<{
    found: boolean;
    cause_list_date: string | null;
    matches: Record<string, { bench_key: string; serial_no: number | null; pdf_url: string | null }>;
  }> {
    return this.http.post<any>(`${app_url}/api/v1/listing/cause-lists/published/latest/lookup/`, { case_numbers });
  }

  lookupNextPublishedForCases(case_numbers: string[]): Observable<{
    matches: Record<
      string,
      { cause_list_date: string; bench_key: string; serial_no: number | null; pdf_url: string | null }
    >;
  }> {
    return this.http.post<any>(`${app_url}/api/v1/listing/cause-lists/published/next/lookup/`, { case_numbers });
  }

  lookupEntryByCaseNumber(
    cause_list_date: string,
    case_number: string,
  ): Observable<{
    found: boolean;
    cause_list_id?: number;
    bench_key?: string;
    serial_no?: number | null;
    pdf_url?: string | null;
  }> {
    const url = `${app_url}/api/v1/listing/cause-lists/entry/?cause_list_date=${encodeURIComponent(
      cause_list_date,
    )}&case_number=${encodeURIComponent(case_number)}`;
    return this.http.get<any>(url);
  }

  getRegisteredCases(params?: { page_size?: number }): Observable<{ total: number; items: RegisteredCase[] }> {
    let url = `${app_url}/api/v1/listing/registered-cases/`;
    if (params?.page_size != null) {
      url += `?page_size=${params.page_size}`;
    }
    return this.http.get<any>(url);
  }

  assignBenches(assignments: { efiling_id: number; bench_key: string }[]): Observable<{ updated: number }> {
    return this.http.post<{ updated: number }>(`${app_url}/api/v1/listing/registered-cases/assign-bench/`, {
      assignments,
    });
  }
}

