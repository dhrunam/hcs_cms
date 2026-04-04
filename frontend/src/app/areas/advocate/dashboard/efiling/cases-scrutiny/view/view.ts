import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ChatReadStateService } from '../../../../../../services/chat/chat-read-state.service';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
interface PendingCase {
  id: number;
  caseTitle: string;
  filingType: string;
  filedOn: string;
  status: string;
}

@Component({
  selector: 'app-view',
  imports: [CommonModule, RouterLink],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class View {
  filingsUnderScrutiny: any[] | null = null;

  get hasCases(): boolean {
    return Array.isArray(this.filingsUnderScrutiny) && this.filingsUnderScrutiny.length > 0;
  }

  constructor(
    private eFilingService: EfilingService,
    private chatReadStateService: ChatReadStateService,
  ) {}

  ngOnInit() {
    this.get_filings_under_scrutiny();
  }

  get_filings_under_scrutiny() {
    this.eFilingService.get_filings_under_scrutiny().subscribe({
      next: (data) => {
        this.filingsUnderScrutiny = data?.results ?? [];
        console.log(this.filingsUnderScrutiny);
      },
    });
  }

  getStatusLabel(status: string | null): string {
    const normalizedStatus = (status ?? '').trim().toLowerCase();
    if (
      !normalizedStatus ||
      normalizedStatus === 'submitted' ||
      normalizedStatus === 'under_scrutiny'
    ) {
      return 'Under Scrutiny';
    }
    if (normalizedStatus.includes('accept')) {
      return 'Accepted';
    }
    if (normalizedStatus.includes('partially')) {
      return 'Partially Rejected';
    }
    if (normalizedStatus.includes('reject') || normalizedStatus.includes('object')) {
      return 'Rejected';
    }
    return status ?? 'Under Scrutiny';
  }

  getStatusBadgeClass(status: string | null): string {
    const label = this.getStatusLabel(status).toLowerCase();
    if (label.includes('accept')) {
      return 'status-badge-success';
    }
    if (label.includes('reject') || label.includes('partial')) {
      return 'status-badge-danger';
    }
    return 'status-badge-warning';
  }

  hasUnreadChat(filing: any): boolean {
    const filingId = Number(filing?.id);
    const latestMessageId = Number(filing?.latest_chat_message_id || 0);
    if (!Number.isFinite(filingId) || latestMessageId <= 0) {
      return false;
    }
    if (filing?.latest_chat_is_from_current_user) {
      return false;
    }
    const lastSeenId = this.chatReadStateService.getLastSeenMessageId(filingId, 'advocate');
    return latestMessageId > lastSeenId;
  }
}
