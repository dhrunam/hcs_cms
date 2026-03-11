import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getCases(params?: Record<string, string | number>): Observable<unknown> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        httpParams = httpParams.set(key, String(value));
      });
    }
    return this.http.get(`${this.baseUrl}/cases/`, { params: httpParams });
  }

  getCase(id: number | string): Observable<unknown> {
    return this.http.get(`${this.baseUrl}/cases/${id}/`);
  }

  createCase(data: unknown): Observable<unknown> {
    return this.http.post(`${this.baseUrl}/cases/`, data);
  }

  updateCase(id: number | string, data: unknown): Observable<unknown> {
    return this.http.put(`${this.baseUrl}/cases/${id}/`, data);
  }

  deleteCase(id: number | string): Observable<unknown> {
    return this.http.delete(`${this.baseUrl}/cases/${id}/`);
  }

  getUserProfile(): Observable<unknown> {
    return this.http.get(`${this.baseUrl}/users/me/`);
  }
}
