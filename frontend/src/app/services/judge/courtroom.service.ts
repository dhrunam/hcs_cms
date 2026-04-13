import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, catchError, throwError } from 'rxjs';
import { app_url } from '../../environment';

@Injectable({ providedIn: 'root' })
export class CourtroomService {
  constructor(private http: HttpClient) {}

  getPendingCases(forwarded_for_date: string): Observable<{
    pending_for_listing: {
      efiling_id: number;
      case_number: string | null;
      bench_key: string;
      bench_label?: string;
      forward_bench_key?: string;
      reader_slot_group?: string;
      listing_summary?: string | null;
      judge_decision: boolean | null;
      judge_decision_status?: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS' | null;
      judge_listing_date: string | null;
      forwarded_for_date?: string;
      courtroom_bucket?: string;
      requested_document_count?: number;
      requested_documents?: { document_index_id: number; document_part_name: string | null; document_type: string | null }[];
    }[];
    pending_for_causelist: {
      efiling_id: number;
      case_number: string | null;
      bench_key: string;
      bench_label?: string;
      forward_bench_key?: string;
      reader_slot_group?: string;
      listing_summary?: string | null;
      judge_decision: boolean | null;
      judge_decision_status?: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS' | null;
      judge_listing_date: string | null;
      forwarded_for_date?: string;
      courtroom_bucket?: string;
      requested_document_count?: number;
      requested_documents?: { document_index_id: number; document_part_name: string | null; document_type: string | null }[];
    }[];
  }> {
    return this.http.get<any>(
      `${app_url}/api/v1/judge/courtroom/pending/?cause_list_date=${encodeURIComponent(forwarded_for_date)}`,
    );
  }

  /** Published cause list PDFs for the date, scoped to benches this judge is seated on. */
  getPublishedCauseListsForSeatedJudge(cause_list_date: string): Observable<{
    items: { id: number; bench_key: string; included_count: number; pdf_url: string | null }[];
  }> {
    return this.http.get<{
      items: { id: number; bench_key: string; included_count: number; pdf_url: string | null }[];
    }>(
      `${app_url}/api/v1/listing/cause-lists/published/?cause_list_date=${encodeURIComponent(
        cause_list_date,
      )}&for_seated_judge=true`,
    );
  }

  getCaseDocuments(
    efiling_id: number,
    forwarded_for_date: string,
    forward_bench_key?: string | null,
    reader_slot_group?: string | null,
    requested_only: boolean = false,
  ): Observable<{
    items: any[];
  }> {
    const benchPart = forward_bench_key
      ? `&forward_bench_key=${encodeURIComponent(String(forward_bench_key))}`
      : "";
    const slotPart = reader_slot_group
      ? `&reader_slot_group=${encodeURIComponent(String(reader_slot_group))}`
      : "";
    return this.http.get<{ items: any[] }>(
      `${app_url}/api/v1/judge/courtroom/cases/${efiling_id}/documents/?cause_list_date=${encodeURIComponent(
        forwarded_for_date,
      )}${benchPart}${slotPart}&requested_only=${requested_only ? 'true' : 'false'}`,
    );
  }

  getCaseSummary(
    efiling_id: number,
    forwarded_for_date: string,
    forward_bench_key?: string | null,
    reader_slot_group?: string | null,
  ): Observable<{
    efiling_id: number;
    case_number: string | null;
    e_filing_number: string | null;
    petitioner_name: string | null;
    petitioner_contact: string | null;
    bench_key: string;
    bench_label?: string;
    forward_bench_key?: string;
    reader_slot_group?: string;
    forwarded_for_date: string;
    listing_summary?: string | null;
    selected_documents?: {
      document_index_id: number;
      document_part_name: string | null;
      document_type: string | null;
      file_url: string | null;
    }[];
    judge_decision?: {
      status: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS';
      approved: boolean;
      decision_notes: string | null;
      requested_documents: { document_index_id: number; document_part_name: string | null; document_type: string | null }[];
    } | null;
    litigants: { id: number; name: string; is_petitioner: boolean; sequence_number: number | null }[];
    case_details: {
      cause_of_action: string | null;
      date_of_cause_of_action: string | null;
      dispute_state: string | null;
      dispute_district: string | null;
      dispute_taluka: string | null;
    } | null;
  }> {
    const benchPart = forward_bench_key
      ? `&forward_bench_key=${encodeURIComponent(String(forward_bench_key))}`
      : "";
    const slotPart = reader_slot_group
      ? `&reader_slot_group=${encodeURIComponent(String(reader_slot_group))}`
      : "";
    return this.http.get<any>(
      `${app_url}/api/v1/judge/courtroom/cases/${efiling_id}/summary/?cause_list_date=${encodeURIComponent(
        forwarded_for_date,
      )}${benchPart}${slotPart}`,
    );
  }

  fetchDocumentBlob(fileUrl: string): Observable<Blob> {
    const candidates = this.buildDocumentUrlCandidates(fileUrl);
    return this.http.get(candidates[0], { responseType: 'blob' }).pipe(
      catchError((firstErr) => {
        if (candidates.length < 2) {
          return throwError(() => firstErr);
        }
        return this.http.get(candidates[1], { responseType: 'blob' });
      }),
    );
  }

  fetchDocumentBlobByIndex(documentIndexId: number): Observable<Blob> {
    return this.http.get(
      `${app_url}/api/v1/efiling/efiling-documents-index/${documentIndexId}/stream/`,
      { responseType: 'blob' },
    );
  }

  resolveDocumentUrl(fileUrl: string): string {
    const raw = String(fileUrl ?? '').trim();
    if (!raw) return raw;
    if (raw.startsWith('http://') || raw.startsWith('https://')) return raw;
    if (raw.startsWith('/media/')) return `${app_url}${raw}`;
    if (raw.startsWith('media/')) return `${app_url}/${raw}`;
    if (raw.startsWith('/')) return `${app_url}${raw}`;
    return `${app_url}/${raw}`;
  }

  private buildDocumentUrlCandidates(fileUrl: string): string[] {
    const primary = this.resolveDocumentUrl(fileUrl);
    const out = [primary];
    try {
      const u = new URL(primary);
      const parts = u.pathname.split('/');
      if (parts.length >= 4) {
        const docTypeIdx = parts.length - 2;
        const docType = parts[docTypeIdx] || '';
        const upper = docType.toUpperCase();
        const lower = docType.toLowerCase();
        if (upper && upper !== docType) {
          const p2 = [...parts];
          p2[docTypeIdx] = upper;
          out.push(`${u.origin}${p2.join('/')}`);
        }
        if (lower && lower !== docType) {
          const p3 = [...parts];
          p3[docTypeIdx] = lower;
          out.push(`${u.origin}${p3.join('/')}`);
        }
      }
    } catch {
      // keep primary only
    }
    return Array.from(new Set(out));
  }

  saveDocumentAnnotation(payload: {
    efiling_document_index_id: number;
    annotation_text?: string | null;
    annotation_data?: any;
  }): Observable<{ efiling_document_index: number; annotation_text: string | null; annotation_data: any }> {
    return this.http.post<{ efiling_document_index: number; annotation_text: string | null; annotation_data: any }>(
      `${app_url}/api/v1/judge/courtroom/document-annotations/`,
      payload,
    );
  }

  saveDecision(payload: {
    efiling_id: number;
    forwarded_for_date: string;
    forward_bench_key?: string;
    decision_notes?: string | null;
    requested_document_index_ids?: number[];
  }): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/judge/courtroom/decisions/`, payload);
  }

  getDecisionCalendar(): Observable<{
    items: {
      efiling_id: number;
      case_number: string | null;
      status: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS';
      approved: boolean;
      listing_date: string | null;
      forwarded_for_date: string | null;
      decision_notes: string | null;
    }[];
  }> {
    return this.http.get<any>(`${app_url}/api/v1/judge/courtroom/decisions/calendar/`);
  }

  updateSharedView(payload: { efiling_id: number; document_index_id: number; page_index: number }): Observable<any> {
    return this.http.post(`${app_url}/api/v1/judge/courtroom/shares/`, payload);
  }

  stopSharedView(efiling_id: number): Observable<any> {
    return this.http.delete(`${app_url}/api/v1/judge/courtroom/shares/?efiling_id=${efiling_id}`);
  }

  getActiveSharedView(efiling_id: number): Observable<any> {
    return this.http.get(`${app_url}/api/v1/judge/courtroom/shares/?efiling_id=${efiling_id}`);
  }

  getStenoWorkflows(): Observable<{ items: any[] }> {
    return this.http.get<{ items: any[] }>(`${app_url}/api/v1/judge/steno-workflows/`);
  }

  /** Replace canvas/positional mark-up; preserves text-only notes (no page, no x/y). */
  saveStenoWorkflowAnnotationsSnapshot(payload: {
    workflow_id: number;
    annotations: Array<{
      page_number?: number | null;
      note_text: string;
      annotation_type: 'COMMENT' | 'HIGHLIGHT' | 'TEXT_REPLACE' | 'FORMAT';
      x?: number | null;
      y?: number | null;
      width?: number | null;
      height?: number | null;
    }>;
  }): Observable<{ saved: number }> {
    return this.http.post<{ saved: number }>(
      `${app_url}/api/v1/judge/steno-workflows/annotations/snapshot/`,
      payload,
    );
  }

  addStenoWorkflowAnnotation(payload: {
    workflow_id: number;
    note_text: string;
    annotation_type?: 'COMMENT' | 'HIGHLIGHT' | 'TEXT_REPLACE' | 'FORMAT';
    page_number?: number | null;
    x?: number | null;
    y?: number | null;
    width?: number | null;
    height?: number | null;
  }): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/judge/steno-workflows/annotations/`, payload);
  }

  decideStenoWorkflow(payload: {
    workflow_id: number;
    judge_approval_status: 'APPROVED' | 'REJECTED';
    judge_approval_notes?: string | null;
  }): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/judge/steno-workflows/decision/`, payload);
  }
}

