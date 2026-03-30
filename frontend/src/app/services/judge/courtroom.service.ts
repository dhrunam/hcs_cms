import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { app_url } from '../../environment';

@Injectable({ providedIn: 'root' })
export class CourtroomService {
  constructor(private http: HttpClient) {}

  getPendingCases(forwarded_for_date: string): Observable<{
    pending_for_listing: {
      efiling_id: number;
      case_number: string | null;
      bench_key: string;
      listing_summary?: string | null;
      judge_decision: boolean | null;
      judge_decision_status?: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS' | null;
      judge_listing_date: string | null;
      forwarded_for_date?: string;
      requested_document_count?: number;
      requested_documents?: { document_index_id: number; document_part_name: string | null; document_type: string | null }[];
    }[];
    pending_for_causelist: {
      efiling_id: number;
      case_number: string | null;
      bench_key: string;
      listing_summary?: string | null;
      judge_decision: boolean | null;
      judge_decision_status?: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS' | null;
      judge_listing_date: string | null;
      forwarded_for_date?: string;
      requested_document_count?: number;
      requested_documents?: { document_index_id: number; document_part_name: string | null; document_type: string | null }[];
    }[];
  }> {
    return this.http.get<any>(
      `${app_url}/api/v1/judge/courtroom/pending/?forwarded_for_date=${encodeURIComponent(forwarded_for_date)}`,
    );
  }

  getCaseDocuments(
    efiling_id: number,
    forwarded_for_date: string,
  ): Observable<{
    items: any[];
  }> {
    return this.http.get<{ items: any[] }>(
      `${app_url}/api/v1/judge/courtroom/cases/${efiling_id}/documents/?forwarded_for_date=${encodeURIComponent(
        forwarded_for_date,
      )}`,
    );
  }

  getCaseSummary(
    efiling_id: number,
    forwarded_for_date: string,
  ): Observable<{
    efiling_id: number;
    case_number: string | null;
    e_filing_number: string | null;
    petitioner_name: string | null;
    petitioner_contact: string | null;
    bench_key: string;
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
      listing_date: string | null;
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
    return this.http.get<any>(
      `${app_url}/api/v1/judge/courtroom/cases/${efiling_id}/summary/?forwarded_for_date=${encodeURIComponent(
        forwarded_for_date,
      )}`,
    );
  }

  saveDocumentAnnotation(payload: {
    efiling_document_index_id: number;
    annotation_text: string | null | undefined;
  }): Observable<{ efiling_document_index: number; annotation_text: string | null }> {
    return this.http.post<{ efiling_document_index: number; annotation_text: string | null }>(
      `${app_url}/api/v1/judge/courtroom/document-annotations/`,
      payload,
    );
  }

  saveDecision(payload: {
    efiling_id: number;
    forwarded_for_date: string;
    listing_date: string;
    status: 'APPROVED' | 'DECLINED' | 'REQUESTED_DOCS';
    decision_notes?: string | null;
    requested_document_index_ids?: number[];
  }): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/judge/courtroom/decisions/`, payload);
  }
}

