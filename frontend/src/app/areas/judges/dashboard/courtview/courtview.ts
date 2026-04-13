import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { Router } from "@angular/router";

import { CourtroomService } from "../../../../services/judge/courtroom.service";
import { benchLabel } from "../../../listing-officers/shared/bench-labels";

/** YYYY-MM-DD in the user's local calendar (avoids UTC day skew from `toISOString()`). */
function localCalendarDateIsoString(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

@Component({
  selector: "app-judge-courtview-cases",
  imports: [CommonModule, FormsModule],
  templateUrl: "./courtview.html",
  styleUrl: "./courtview.css",
})
export class JudgeCourtviewPage {
  benchLabel = benchLabel;
  forwardedForDate: string = localCalendarDateIsoString();
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
        const published = resp?.pending_for_causelist ?? [];
        const prePublish = resp?.pending_for_listing ?? [];
        this.listedCases = [...published, ...prePublish];
        this.isLoading = false;
        this.loadError = "";
      },
      error: (err) => {
        console.warn("Failed to load judge hearings", err);
        this.loadError = "Failed to load listed cases.";
        this.isLoading = false;
      },
    });
  }

  courtroomBucketLabel(c: { courtroom_bucket?: string }): string {
    if (c.courtroom_bucket === "pre_publish_listing") {
      return "Pre-hearing (not on published list)";
    }
    if (c.courtroom_bucket === "published_causelist") {
      return "Published cause list";
    }
    return "";
  }

  /** Uses the selected Hearing Date so detail views align with this list (not the forward row date). */
  openCourtroom(efilingId: number): void {
    this.router.navigate(["/judges/dashboard/courtview/case", efilingId], {
      queryParams: { forwarded_for_date: this.forwardedForDate },
    });
  }
}
