import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { app_url } from '../environment';

const AUTH_BASE = `${app_url}/api/v1/accounts/auth`;

export interface RegistrationSuccessPayload {
  id?: number;
  email?: string;
  detail?: string;
  email_verification_required?: boolean;
  verification_token?: string;
  /** When true, backend created the user with `is_active=false` until an admin verifies ID proof. */
  requires_admin_activation?: boolean;
}

export function formatRegistrationError(err: unknown): string {
  if (!(err instanceof HttpErrorResponse)) {
    return 'Something went wrong. Please try again.';
  }
  const body = err.error;
  if (body && typeof body === 'object' && body !== null) {
    if ('detail' in body && typeof (body as { detail: unknown }).detail === 'string') {
      return (body as { detail: string }).detail;
    }
    const parts: string[] = [];
    for (const [key, val] of Object.entries(body)) {
      if (key === 'detail') continue;
      if (key === 'non_field_errors' && Array.isArray(val)) {
        parts.push(val.join(' '));
        continue;
      }
      if (Array.isArray(val)) {
        parts.push(`${key}: ${val.join(' ')}`);
      } else if (typeof val === 'string') {
        parts.push(`${key}: ${val}`);
      }
    }
    if (parts.length) {
      return parts.join(' ');
    }
  }
  return err.message || 'Request failed.';
}

@Injectable({ providedIn: 'root' })
export class RegistrationService {
  private http = inject(HttpClient);

  registerParty(formData: FormData): Observable<RegistrationSuccessPayload> {
    return this.http.post<RegistrationSuccessPayload>(`${AUTH_BASE}/register/party/`, formData);
  }

  registerAdvocate(formData: FormData): Observable<RegistrationSuccessPayload> {
    return this.http.post<RegistrationSuccessPayload>(`${AUTH_BASE}/register/advocate/`, formData);
  }

  verifyEmail(token: string): Observable<{ detail?: string }> {
    return this.http.post<{ detail?: string }>(`${AUTH_BASE}/verify-email/`, { token });
  }
}
