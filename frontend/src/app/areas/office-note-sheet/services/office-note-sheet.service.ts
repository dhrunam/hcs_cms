import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { app_url } from '../../../environment';

export interface OfficeNote {
  id: number;
  case_id: number;
  case_number: string;
  note_content: string;
  created_by: number;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
}

export interface CaseItem {
  id: number;
  case_number: string;
  petitioner_name: string;
  respondent_name?: string;
  status: string;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class OfficeNoteSheetService {
  constructor(private http: HttpClient) {}

  getCases(params?: { page_size?: number; search?: string }): Observable<{ results: CaseItem[] }> {
    let url = `${app_url}/api/v1/efiling/efilings/?is_draft=false&status=ACCEPTED`;
    if (params?.page_size) {
      url += `&page_size=${params.page_size}`;
    }
    if (params?.search) {
      url += `&search=${encodeURIComponent(params.search)}`;
    }
    return this.http.get<{ results: CaseItem[] }>(url);
  }

  getNotesByCaseId(caseId: number): Observable<OfficeNote[]> {
    return this.http.get<OfficeNote[]>(
      `${app_url}/api/v1/office-notes/?case_id=${caseId}`,
    );
  }

  createNote(payload: { case_id: number; note_content: string }): Observable<OfficeNote> {
    return this.http.post<OfficeNote>(
      `${app_url}/api/v1/office-notes/`,
      payload,
    );
  }

  updateNote(noteId: number, payload: { note_content: string }): Observable<OfficeNote> {
    return this.http.patch<OfficeNote>(
      `${app_url}/api/v1/office-notes/${noteId}/`,
      payload,
    );
  }
}