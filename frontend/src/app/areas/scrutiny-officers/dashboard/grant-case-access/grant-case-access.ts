import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import {
  CaseAccessRequestItem,
  EfilingService,
} from "../../../../services/advocate/efiling/efiling.services";
import { app_url } from "../../../../environment";

@Component({
  selector: "app-grant-case-access",
  standalone: true,
  imports: [CommonModule],
  templateUrl: "./grant-case-access.html",
  styleUrl: "./grant-case-access.css",
})
export class GrantCaseAccess {
  items: CaseAccessRequestItem[] = [];
  isLoading = false;
  errorMessage = "";
  actionMessage = "";

  constructor(private efilingService: EfilingService) {}

  ngOnInit(): void {
    this.loadRequests();
  }

  loadRequests(): void {
    this.isLoading = true;
    this.errorMessage = "";
    this.efilingService.get_case_access_requests().subscribe({
      next: (payload) => {
        this.isLoading = false;
        this.items = this.extractItems(payload);
      },
      error: () => {
        this.isLoading = false;
        this.items = [];
        this.errorMessage = "Unable to load requests. Ensure your user has Scrutiny Officer role.";
      },
    });
  }

  approve(item: CaseAccessRequestItem): void {
    this.actionMessage = "";
    this.efilingService
      .review_case_access_request(item.id, { status: "APPROVED" })
      .subscribe({
        next: () => {
          this.actionMessage = `Request ${item.case_number} approved successfully.`;
          this.loadRequests();
        },
        error: (error) => {
          this.actionMessage =
            error?.error?.detail ||
            error?.error?.status?.[0] ||
            "Unable to approve request. Please verify your scrutiny officer permissions.";
        },
      });
  }

  reject(item: CaseAccessRequestItem): void {
    const reason = window.prompt("Enter rejection reason");
    if (!reason || !reason.trim()) {
      return;
    }
    this.actionMessage = "";
    this.efilingService
      .review_case_access_request(item.id, {
        status: "REJECTED",
        rejection_reason: reason.trim(),
      })
      .subscribe({
        next: () => {
          this.actionMessage = `Request ${item.case_number} rejected.`;
          this.loadRequests();
        },
        error: (error) => {
          this.actionMessage =
            error?.error?.detail ||
            error?.error?.rejection_reason?.[0] ||
            "Unable to reject request.";
        },
      });
  }

  documentUrl(item: CaseAccessRequestItem): string | null {
    const raw = String((item as any)?.vakalatnama_document || "").trim();
    if (!raw) return null;
    if (raw.startsWith("http://") || raw.startsWith("https://")) return raw;
    if (raw.startsWith("/")) return `${app_url}${raw}`;
    return `${app_url}/${raw}`;
  }

  private extractItems(payload: { results?: CaseAccessRequestItem[] } | CaseAccessRequestItem[]): CaseAccessRequestItem[] {
    if (Array.isArray(payload)) {
      return payload;
    }
    if (Array.isArray(payload?.results)) {
      return payload.results;
    }
    return [];
  }
}
