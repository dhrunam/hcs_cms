import { HttpClient } from '@angular/common/http';
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
  delete_case_documnets_before_final_filing(id: number): Observable<any> {
    return this.http.delete<any>(`${app_url}/api/v1/efiling/efiling-documents/${id}/`);
  }

  final_submit_efiling(id: number): Observable<any> {
    var fd = new FormData();
    fd.append('is_draft', 'false');
    return this.http.patch<any>(`${app_url}/api/v1/efiling/efilings/28/`, fd);
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
}
