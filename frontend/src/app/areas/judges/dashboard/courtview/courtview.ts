import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { Router } from "@angular/router";

import { CourtroomService } from "../../../../services/judge/courtroom.service";
import { benchLabel } from "../../../listing-officers/shared/bench-labels";

@Component({
  selector: "app-judge-courtview-cases",
  imports: [CommonModule, FormsModule],
  templateUrl: "./courtview.html",
  styleUrl: "./courtview.css",
})
export class JudgeCourtviewPage {
  benchLabel = benchLabel;
  forwardedForDate: string = new Date().toISOString().slice(0, 10);
  isLoading = false;
  loadError = "";

  listedCases: any[] = [];

  constructor(
    private courtroomService: CourtroomService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.load();
  }

  onDateChange(): void {
    this.load();
  }

  private load(): void {
    this.isLoading = true;
    this.loadError = "";

    this.courtroomService.getPendingCases(this.forwardedForDate).subscribe({
      next: (resp) => {
        // Unified API returns cases in 'pending_for_causelist' once published/forwarded
        this.listedCases = resp?.pending_for_causelist ?? [];
        console.log("Listed case for today is", this.listedCases);
        this.isLoading = false;
        if (this.listedCases.length === 0) {
          this.loadError = "No published hearings found for this date.";
        }
      },
      error: (err) => {
        console.warn("Failed to load judge hearings", err);
        this.loadError = "Failed to load listed cases.";
        this.isLoading = false;
      },
    });
  }

  openCourtroom(
    efilingId: number,
    forwardedDate: string | null | undefined,
  ): void {
    const fdate = forwardedDate || this.forwardedForDate;
    this.router.navigate(["/judges/dashboard/courtview/case", efilingId], {
      queryParams: { forwarded_for_date: fdate },
    });
  }
}
