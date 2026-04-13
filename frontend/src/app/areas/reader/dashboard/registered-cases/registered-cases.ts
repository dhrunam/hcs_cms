import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { Router } from "@angular/router";
import { catchError, of } from "rxjs";

import {
  BenchConfiguration,
  ReaderService,
  RegisteredCase,
  resolveBenchConfiguration,
} from "../../../../services/reader/reader.service";

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
    this.readerService.getBenchConfigurations({ accessible_only: true }).subscribe({
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
    const o = c.overall_status;
    if (o === "ready_for_listing") {
      return "Ready for listing";
    }
    if (o === "in_review") {
      if (
        c.my_forward_status === "not_forwarded" &&
        c.bench_has_forward === true
      ) {
        return "Your summary not sent";
      }
      return "Waiting for judge(s)";
    }
    if (o === "not_forwarded") {
      return "Pending forward";
    }
    if (o === "rejected") return "Judge rejected";
    if (o === "requested_docs") return "Docs requested";
    switch (c.approval_status) {
      case "APPROVED":
        return "Judge approved";
      case "REJECTED":
        return "Judge rejected";
      case "REQUESTED_DOCS":
        return "Docs requested";
      case "PENDING":
        return "Waiting for judge(s)";
      default:
        return "Pending forward";
    }
  }

  approvalIcon(c: RegisteredCase): string {
    if (c.approval_listing_date) return "fa-check-double";
    const o = c.overall_status;
    if (o === "ready_for_listing") return "fa-check";
    if (o === "in_review") return "fa-clock";
    if (o === "not_forwarded") return "fa-paper-plane";
    if (o === "rejected") return "fa-xmark";
    if (o === "requested_docs") return "fa-file-circle-question";
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
    const o = c.overall_status;
    if (o === "ready_for_listing") return "text-bg-success";
    if (o === "in_review") return "text-bg-warning";
    if (o === "not_forwarded") return "text-bg-primary";
    if (o === "rejected") return "text-bg-danger";
    if (o === "requested_docs") return "text-bg-warning";
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
    const ready =
      c.overall_status === "ready_for_listing" ||
      c.approval_status === "APPROVED";
    return (
      ready &&
      !c.approval_listing_date &&
      c.can_assign_listing_date === false
    );
  }

  openCase(efilingId: number): void {
    this.router.navigate(["/reader/dashboard/case", efilingId]);
  }
}
