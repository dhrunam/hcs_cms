import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { app_url } from '../../environment';

export interface ChatMessageItem {
  id: number;
  e_filing: number;
  sender: number | null;
  sender_name: string;
  sender_email: string | null;
  sender_role: 'advocate' | 'scrutiny_officer' | 'system' | 'user';
  message: string;
  created_at: string;
  updated_at: string | null;
  is_current_user: boolean;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  constructor(private http: HttpClient) {}

  getMessages(filingId: number): Observable<ChatMessageItem[]> {
    return this.http.get<ChatMessageItem[]>(
      `${app_url}/api/v1/efiling/efilings/${filingId}/chat-messages/`,
    );
  }

  sendMessage(filingId: number, message: string): Observable<ChatMessageItem> {
    return this.http.post<ChatMessageItem>(
      `${app_url}/api/v1/efiling/efilings/${filingId}/chat-messages/`,
      { message },
    );
  }
}