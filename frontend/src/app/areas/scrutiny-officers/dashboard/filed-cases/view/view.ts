import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, forkJoin, of } from 'rxjs';
import { EfilingService } from '../../../../../services/advocate/efiling/efiling.services';
import { ChatReadStateService } from '../../../../../services/chat/chat-read-state.service';

interface EfilingCaseType {
  type_name?: string;
}

interface EfilingItem {
  id: number;
  petitioner_vs_respondent?: string | null;
  petitioner_name: string;
  petitioner_contact: string;
  e_filing_number: string;
  case_number?: string | null;
  created_at: string;
  status: string | null;
  bench: string | null;
  case_type: EfilingCaseType | null;
  latest_chat_message_id?: number | null;
  latest_chat_message_at?: string | null;
  latest_chat_is_from_current_user?: boolean;
}

@Component({
  selector: 'app-filed-cases-view',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './view.html',
  styleUrl: './view.css',
})
export class FiledCasesView {
  allCases: EfilingItem[] = [];
  newIncomingFilingIds = new Set<number>();
  urgentFilingIds = new Set<number>();
  isLoading = false;
  mode: 'all' | 'registered' = 'all';

  constructor(
    private eFilingService: EfilingService,
    private route: ActivatedRoute,
    private chatReadStateService: ChatReadStateService,
  ) {}

  ngOnInit(): void {
    this.mode = this.route.snapshot.data['mode'] === 'registered' ? 'registered' : 'all';
    this.getFiledCases();
  }

  getFiledCases(): void {
    this.isLoading = true;
    forkJoin({
      filings: this.eFilingService.get_scrutiny_cases(),
      incoming: this.eFilingService.get_new_scrutiny_documents().pipe(
        catchError((error) => {
          console.warn('Failed to load new scrutiny documents', error);
          return of([]);
        }),
      ),
    }).subscribe({
      next: ({ filings, incoming }) => {
        this.allCases = this.extractItems(filings);
        this.newIncomingFilingIds = new Set<number>(
          this.extractItems(incoming)
            .map((item: any) => item?.e_filing_id)
            .filter((id: number | null | undefined) => typeof id === 'number'),
        );
        this.markUrgentCasesFromMemoOfAppeal();
      },
      error: (error) => {
        console.error('Failed to load filed cases', error);
        this.allCases = [];
        this.newIncomingFilingIds = new Set<number>();
        this.urgentFilingIds = new Set<number>();
        this.isLoading = false;
      },
    });
  }

  private markUrgentCasesFromMemoOfAppeal(): void {
    const filings = Array.isArray(this.allCases) ? this.allCases : [];
    const requests = filings
      .filter((filing) => Number.isFinite(Number(filing?.id)))
      .map((filing) =>
        this.eFilingService.get_document_reviews_by_filing_id(Number(filing.id), false).pipe(
          catchError(() => of([])),
        ),
      );

    if (requests.length === 0) {
      this.urgentFilingIds = new Set<number>();
      this.isLoading = false;
      return;
    }

    forkJoin(requests).subscribe({
      next: (responses) => {
        const urgentIds = new Set<number>();
        filings.forEach((filing, index) => {
          const payload = responses[index];
          const items = this.extractItems(payload);
          const hasMemo = items.some((item: any) => {
            const typeName = String(item?.document_type || '').trim().toLowerCase();
            const partName = String(item?.document_part_name || '').trim().toLowerCase();
            return typeName === 'memo of appeal' || partName.includes('memo of appeal');
          });
          if (hasMemo) {
            urgentIds.add(Number(filing.id));
          }
        });
        this.urgentFilingIds = urgentIds;
        this.isLoading = false;
      },
      error: () => {
        this.urgentFilingIds = new Set<number>();
        this.isLoading = false;
      },
    });
  }

  private extractItems(payload: any): any[] {
    if (Array.isArray(payload)) {
      return payload;
    }
    if (Array.isArray(payload?.results)) {
      return payload.results;
    }
    return [];
  }

  get filedCases(): EfilingItem[] {
    return this.allCases.filter((filing) => !filing.case_number);
  }

  get registeredCases(): EfilingItem[] {
    return this.allCases.filter((filing) => !!filing.case_number);
  }

  get showFiledCasesSection(): boolean {
    return this.mode !== 'registered';
  }

  get showRegisteredCasesSection(): boolean {
    return this.mode === 'registered';
  }

  hasNewForScrutiny(filingId: number | null | undefined): boolean {
    const id = Number(filingId);
    return Number.isFinite(id) && this.newIncomingFilingIds.has(id);
  }

  isUrgent(filingId: number | null | undefined): boolean {
    const id = Number(filingId);
    return Number.isFinite(id) && this.urgentFilingIds.has(id);
  }

  isUrgentCase(filing: EfilingItem | null | undefined): boolean {
    const id = Number(filing?.id);
    return Number.isFinite(id) && this.urgentFilingIds.has(id);
  }

  hasUnreadChat(filing: EfilingItem | null | undefined): boolean {
    const filingId = Number(filing?.id);
    const latestMessageId = Number(filing?.latest_chat_message_id || 0);
    if (!Number.isFinite(filingId) || latestMessageId <= 0) {
      return false;
    }
    if (filing?.latest_chat_is_from_current_user) {
      return false;
    }
    const lastSeenId = this.chatReadStateService.getLastSeenMessageId(filingId, 'scrutiny_officer');
    return latestMessageId > lastSeenId;
  }

  getStatusLabel(item: EfilingItem): string {
    const status = item.status || '';
    const normalizedStatus = status.trim().toLowerCase();

    if (normalizedStatus.includes('accepted')) {
      if (!item.bench || item.bench === 'null' || item.bench === 'undefined') {
        return 'Returned / Bench Needed';
      }
      return 'Accepted / Assigned';
    }

    if (!normalizedStatus || normalizedStatus === 'submitted' || normalizedStatus === 'under_scrutiny') {
      return 'Under Scrutiny';
    }

    if (normalizedStatus.includes('partially')) {
      return 'Partially Rejected';
    }

    if (
      normalizedStatus.includes('rejected') ||
      normalizedStatus.includes('object') ||
      normalizedStatus.includes('defect')
    ) {
      return 'Rejected';
    }

    return status || 'Under Scrutiny';
  }

  getStatusTone(item: EfilingItem): 'warning' | 'success' | 'danger' | 'info' {
    const status = item.status || '';
    const normalizedStatus = status.trim().toLowerCase();

    if (normalizedStatus.includes('accepted')) {
      if (!item.bench || item.bench === 'null' || item.bench === 'undefined') {
        return 'info';
      }
      return 'success';
    }

    if (!normalizedStatus || normalizedStatus === 'submitted' || normalizedStatus === 'under_scrutiny') {
      return 'warning';
    }

    if (
      normalizedStatus.includes('partially') ||
      normalizedStatus.includes('rejected') ||
      normalizedStatus.includes('object') ||
      normalizedStatus.includes('defect')
    ) {
      return 'danger';
    }
    return 'warning';
  }
}
