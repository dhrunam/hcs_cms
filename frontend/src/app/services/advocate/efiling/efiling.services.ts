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
}
