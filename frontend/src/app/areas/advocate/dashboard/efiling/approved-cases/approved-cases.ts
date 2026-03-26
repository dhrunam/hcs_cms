import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { EfilingService } from '../../../../../services/advocate/efiling/efiling.services';
import { CauseListService } from '../../../../../services/listing/cause-list.service';

@Component({
  selector: 'app-approved-cases',
  imports: [CommonModule, RouterLink],
  templateUrl: './approved-cases.html',
  styleUrl: './approved-cases.css',
})
export class ApprovedCases {
  approvedCases: any[] | null = null;
  causeListMatches: Record<
    string,
    { cause_list_date: string; pdf_url: string | null; bench_key: string; serial_no: number | null }
  > = {};
  private readonly benchLabels: Record<string, string> = {
    CJ: "Hon'ble Chief Justice",
    Judge1: "Hon'ble Judge - I",
    Judge2: "Hon'ble Judge - II",
    'CJ+Judge1': 'Division Bench I',
    'CJ+Judge2': 'Division Bench II',
    'Judge1+Judge2': 'Division Bench III',
    'CJ+Judge1+Judge2': 'Full Bench',
  };

  get hasCases(): boolean {
    return Array.isArray(this.approvedCases) && this.approvedCases.length > 0;
  }

  constructor(
    private eFilingService: EfilingService,
    private causeListService: CauseListService,
  ) {}

  ngOnInit() {
    this.get_approved_cases();
  }

  get_approved_cases() {
    this.eFilingService.get_approved_cases().subscribe({
      next: (data) => {
        this.approvedCases = data?.results ?? [];
        this.loadNextCauseListInfo();
      },
    });
  }

  private loadNextCauseListInfo(): void {
    const caseNumbers: string[] = (this.approvedCases ?? [])
      .map((c) => String(c?.case_number || '').trim())
      .filter((x) => x.length > 0);

    if (caseNumbers.length === 0) {
      this.causeListMatches = {};
      return;
    }

    this.causeListService.lookupNextPublishedForCases(caseNumbers).subscribe({
      next: (lookup) => {
        this.causeListMatches = lookup?.matches ?? {};
      },
      error: () => {
        this.causeListMatches = {};
      },
    });
  }

  getCauseListLink(caseNumber: string | null | undefined): string | null {
    const cn = String(caseNumber || '').trim();
    if (!cn) return null;
    const match = this.causeListMatches[cn];
    return match?.pdf_url ?? null;
  }

  getCauseListDate(caseNumber: string | null | undefined): string | null {
    const cn = String(caseNumber || '').trim();
    if (!cn) return null;
    const match = this.causeListMatches[cn];
    return match?.cause_list_date ?? null;
  }

  getCauseListTooltip(caseNumber: string | null | undefined): string | null {
    const cn = String(caseNumber || '').trim();
    if (!cn) return null;
    const match = this.causeListMatches[cn];
    if (!match) return null;
    const benchLabel = this.benchLabels[match.bench_key] ?? match.bench_key;
    const sr = match.serial_no != null ? String(match.serial_no) : '-';
    const date = match.cause_list_date ? ` (${match.cause_list_date})` : '';
    return `${benchLabel} • Sr ${sr}${date}`;
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
      return 'background: #f1f5f9; color: #1e293b';
    }
    if (label.includes('reject') || label.includes('partial')) {
      return 'background: #fee2e2; color: #991b1b';
    }
    return 'background: #fef3c7; color: #92400e';
  }
}
