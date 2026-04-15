import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import {
  CaseAccessSearchItem,
  CaseAccessRequestItem,
  EfilingService,
} from "../../../../../services/advocate/efiling/efiling.services";

@Component({
  selector: "app-case-access-requests",
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: "./case-access-requests.html",
  styleUrl: "./case-access-requests.css",
})
export class CaseAccessRequests {
  caseNumber = "";
  vakalatnamaFile: File | null = null;
  items: CaseAccessRequestItem[] = [];
  suggestions: CaseAccessSearchItem[] = [];
  isSubmitting = false;
  errorMessage = "";
  successMessage = "";
  private searchTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(private efilingService: EfilingService) {}

  ngOnInit(): void {
    this.loadRequests();
  }

  loadRequests(): void {
    this.efilingService.get_case_access_requests().subscribe({
      next: (payload) => {
        this.items = this.extractItems(payload);
      },
      error: () => {
        this.items = [];
      },
    });
  }

  onFileChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    const file = target.files && target.files.length > 0 ? target.files[0] : null;
    this.vakalatnamaFile = file;
  }

  onCaseNumberInput(): void {
    const q = this.caseNumber.trim();
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }
    if (q.length < 2) {
      this.suggestions = [];
      return;
    }
    this.searchTimer = setTimeout(() => {
      this.efilingService.search_case_access_candidates(q).subscribe({
        next: (data) => {
          this.suggestions = Array.isArray(data?.items) ? data.items : [];
        },
        error: () => {
          this.suggestions = [];
        },
      });
    }, 250);
  }

  pickSuggestion(item: CaseAccessSearchItem): void {
    this.caseNumber = item.case_number || "";
    this.suggestions = [];
  }

  submitRequest(): void {
    this.errorMessage = "";
    this.successMessage = "";
    if (!this.caseNumber.trim()) {
      this.errorMessage = "Case number is required.";
      return;
    }
    if (!this.vakalatnamaFile) {
      this.errorMessage = "Please upload vakalatnama.";
      return;
    }

    const fd = new FormData();
    fd.append("case_number", this.caseNumber.trim());
    fd.append("vakalatnama_document", this.vakalatnamaFile);

    this.isSubmitting = true;
    this.suggestions = [];
    this.efilingService.create_case_access_request(fd).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.caseNumber = "";
        this.vakalatnamaFile = null;
        this.successMessage = "Case access request submitted.";
        this.loadRequests();
      },
      error: (error) => {
        this.isSubmitting = false;
        this.errorMessage =
          error?.error?.case_number?.[0] ||
          error?.error?.detail ||
          "Unable to submit request.";
      },
    });
  }

  reapply(item: CaseAccessRequestItem): void {
    this.errorMessage = "";
    this.successMessage = "";
    this.efilingService.reapply_case_access_request(item.id).subscribe({
      next: () => {
        this.successMessage = "Reapplication submitted.";
        this.loadRequests();
      },
      error: (error) => {
        this.errorMessage = error?.error?.detail || "Unable to reapply.";
      },
    });
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
