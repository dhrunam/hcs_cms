import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { Router } from "@angular/router";
import { catchError, of } from "rxjs";

import {
  BenchConfiguration,
  ReaderService,
  resolveBenchConfiguration,
} from "../../../../services/reader/reader.service";

type RegisteredCase = {
  efiling_id: number;
  case_number: string | null;
  petitioner_name: string | null;
  respondent_name: string | null;
  petitioner_vs_respondent?: string | null;
  bench: string | null;
  bench_key?: string | null;

  cause_of_action: string | null;
  date_of_cause_of_action: string | null;
  dispute_state: string | null;
  dispute_district: string | null;
  dispute_taluka: string | null;
  approval_status?:
    | "NOT_FORWARDED"
    | "PENDING"
    | "APPROVED"
    | "REJECTED"
    | "REQUESTED_DOCS";
  approval_notes?: string[];
  approval_bench_key?: string | null;
  approval_forwarded_for_date?: string | null;
  approval_listing_date?: string | null;
  listing_summary?: string | null;
  can_assign_listing_date?: boolean;
  requested_documents?: {
    document_index_id: number;
    document_part_name: string | null;
    document_type: string | null;
  }[];
};

@Component({
  selector: "app-registered-cases",
  imports: [CommonModule, FormsModule],
  templateUrl: "./registered-cases.html",
  styleUrl: "./registered-cases.css",
})
export class RegisteredCasesPage {
  isLoading = false;
  cases: RegisteredCase[] = [];
  benchConfigurations: BenchConfiguration[] = [];
  loadError = "";

  constructor(
    private readerService: ReaderService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.loadBenchConfigurations();
    this.loadRegisteredCases();
  }

  private loadBenchConfigurations(): void {
    this.readerService.getBenchConfigurations().subscribe({
      next: (resp) => {
        this.benchConfigurations = resp?.items ?? [];
      },
      error: (err) => {
        console.warn("Failed to load bench configurations", err);
        this.benchConfigurations = [];
      },
    });
  }

  private loadRegisteredCases(): void {
    this.loadError = "";
    this.isLoading = true;

    this.readerService
      .getRegisteredCases({ page_size: 200 })
      .pipe(
        catchError((err) => {
          console.warn("Failed to load registered cases", err);
          this.isLoading = false;
          this.loadError = "Failed to load registered cases.";
          return of({ items: [] });
        }),
      )
      .subscribe((resp) => {
        this.cases = (resp?.items ?? []).map((c: any) => ({ ...c }));
        this.isLoading = false;

        console.log("Register Cases ", this.cases);
      });
  }

  benchLabel(key: string | null | undefined): string {
    if (this.isUnassignedBench(key)) return "-";
    const normalizedKey = String(key ?? "").trim();
    return (
      resolveBenchConfiguration(this.benchConfigurations, normalizedKey)
        ?.label || normalizedKey
    );
  }

  private isUnassignedBench(key: string | null | undefined): boolean {
    const value = String(key ?? "")
      .trim()
      .toLowerCase();
    return (
      !value ||
      value === "high court of sikkim" ||
      value === "high court of skkim"
    );
  }

  approvalStatusLabel(c: RegisteredCase): string {
    if (c.approval_listing_date) return "Forwarded for Listing";
    switch (c.approval_status) {
      case "APPROVED":
        return "Judge Approved";
      case "REJECTED":
        return "Judge Rejected";
      case "REQUESTED_DOCS":
        return "Docs Requested";
      case "PENDING":
        return "Waiting for Judge";
      default:
        return "Pending Forward";
    }
  }

  approvalIcon(c: RegisteredCase): string {
    if (c.approval_listing_date) return "fa-check-double";
    switch (c.approval_status) {
      case "APPROVED":
        return "fa-check";
      case "REJECTED":
        return "fa-xmark";
      case "REQUESTED_DOCS":
        return "fa-file-circle-question";
      case "PENDING":
        return "fa-clock";
      default:
        return "fa-paper-plane";
    }
  }

  approvalBadgeClass(c: RegisteredCase): string {
    switch (c.approval_status) {
      case "APPROVED":
        return "text-bg-success";
      case "REJECTED":
        return "text-bg-danger";
      case "REQUESTED_DOCS":
        return "text-bg-warning";
      case "PENDING":
        return "text-bg-warning";
      default:
        return "text-bg-primary";
    }
  }

  showDivisionBenchAuthorityHint(c: RegisteredCase): boolean {
    return (
      c.approval_status === "APPROVED" &&
      !c.approval_listing_date &&
      c.can_assign_listing_date === false
    );
  }

  openCase(efilingId: number): void {
    this.router.navigate(["/reader/dashboard/case", efilingId]);
  }
}
