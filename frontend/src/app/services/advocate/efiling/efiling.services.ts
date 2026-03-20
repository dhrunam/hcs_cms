import { HttpClient, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Injectable } from '@angular/core';
import { app_url } from '../../../environment';

@Injectable({ providedIn: 'root' })
export class EfilingService {
  constructor(private http: HttpClient) {}

  post_efiling_initial_details(fd: FormData): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/efiling/efilings/`, fd);
  }

  post_litigant_details(fd: FormData): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/efiling/efiling-litigants/`, fd);
  }

  delete_litigant_details_by_id(id: number): Observable<any> {
    return this.http.delete<any>(`${app_url}/api/v1/efiling/efiling-litigants/${id}/`);
  }

  post_case_details(fd: FormData): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/efiling/efiling-case-details/`, fd);
  }

  upload_case_documnets(fd: FormData): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/efiling/efiling-documents/`, fd);
  }

  upload_case_documnets_index(fd: FormData): Observable<HttpEvent<any>> {
    return this.http.post<any>(`${app_url}/api/v1/efiling/efiling-documents-index/`, fd, {
      reportProgress: true,
      observe: 'events',
    });
  }

  delete_case_documnets_before_final_filing(id: number): Observable<any> {
    return this.http.delete<any>(`${app_url}/api/v1/efiling/efiling-documents/${id}/`);
  }

  final_submit_efiling(id: number): Observable<any> {
    var fd = new FormData();
    fd.append('is_draft', 'false');
    return this.http.patch<any>(`${app_url}/api/v1/efiling/efilings/${id}/`, fd);
  }

  add_case_details_act(fd: FormData) {
    return this.http.post<any>(`${app_url}/api/v1/efiling/efiling-acts/`, fd);
  }

  get_filings_under_scrutiny(): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efilings/?is_draft=false`);
  }

  get_filings_under_draft(): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efilings/?is_draft=true`);
  }

  get_filing_by_id(id: number): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efilings/${id}/`);
  }

  submit_approved_filing(id: number): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/efiling/efilings/${id}/submit-approved/`, {});
  }

  get_litigant_list_by_filing_id(id: number): Observable<any> {
    console.log(`${app_url}/api/v1/efiling/efiling-litigants/?efiling_id=${id}`);
    return this.http.get<any>(`${app_url}/api/v1/efiling/efiling-litigants/?efiling_id=${id}`);
  }
  get_case_details_by_filing_id(id: number): Observable<any> {
    console.log(`${app_url}/api/v1/efiling/efiling-case-details/?efiling_id=${id}`);
    return this.http.get<any>(`${app_url}/api/v1/efiling/efiling-case-details/?efiling_id=${id}`);
  }

  get_acts_by_filing_id(id: number): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efiling-acts/?efiling_id=${id}`);
  }

  get_documents_by_filing_id(id: number): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efiling-documents/?efiling_id=${id}`);
  }

  get_efiling_documents(): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efiling-documents/`);
  }

  get_document_reviews_by_filing_id(id: number): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efiling-documents-index/?efiling_id=${id}`);
  }

  get_document_scrutiny_history(documentIndexId: number): Observable<any> {
    return this.http.get<any>(
      `${app_url}/api/v1/efiling/efiling-documents-scrutiny-history/?document_index_id=${documentIndexId}`,
    );
  }

  fetch_document_blob(fileUrl: string): Observable<Blob> {
    return this.http.get(fileUrl, { responseType: 'blob' });
  }

  review_document(documentIndexId: number, payload: FormData | Record<string, any>): Observable<any> {
    return this.http.patch<any>(
      `${app_url}/api/v1/efiling/efiling-documents-index/${documentIndexId}/`,
      payload,
    );
  }

  replace_document(documentId: number, file: File, documentType?: string): Observable<any> {
    const fd = new FormData();
    fd.append('final_document', file);
    if (documentType) {
      fd.append('document_type', documentType);
    }
    return this.http.patch<any>(`${app_url}/api/v1/efiling/efiling-documents/${documentId}/`, fd);
  }

  get_file_scrutiny_checklist(caseTypeId: number): Observable<any> {
    return this.http.get<any>(
      `${app_url}/api/v1/efiling/file-scrutiny-checklists/?case_type=${caseTypeId}`,
    );
  }

  get_document_index_master(): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/document-index/`);
  }
}
