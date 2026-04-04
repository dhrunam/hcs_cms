import { Injectable } from '@angular/core';

export type ChatRoleScope = 'advocate' | 'scrutiny_officer';

@Injectable({ providedIn: 'root' })
export class ChatReadStateService {
  private readonly storagePrefix = 'chat:lastSeen';

  getLastSeenMessageId(filingId: number, role: ChatRoleScope): number {
    const raw = localStorage.getItem(this.buildKey(filingId, role));
    const parsed = raw ? Number(raw) : 0;
    return Number.isFinite(parsed) ? parsed : 0;
  }

  markSeen(filingId: number, role: ChatRoleScope, messageId: number): void {
    if (!Number.isFinite(filingId) || !Number.isFinite(messageId) || messageId <= 0) {
      return;
    }
    localStorage.setItem(this.buildKey(filingId, role), String(messageId));
  }

  private buildKey(filingId: number, role: ChatRoleScope): string {
    return `${this.storagePrefix}:${role}:${filingId}`;
  }
}