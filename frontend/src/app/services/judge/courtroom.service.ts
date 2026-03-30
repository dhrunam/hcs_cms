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
      judge_decision: boolean | null;
      judge_listing_date: string | null;
    }[];
    pending_for_causelist: {
      efiling_id: number;
      case_number: string | null;
      bench_key: string;
      judge_decision: boolean | null;
      judge_listing_date: string | null;
    }[];
  }> {
    return this.http.get<any>(
      `${app_url}/api/v1/judge/courtroom/pending/?forwarded_for_date=${encodeURIComponent(
        forwarded_for_date,
      )}`,
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
    approved: boolean;
    decision_notes?: string | null;
  }): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/judge/courtroom/decisions/`, payload);
  }
}

