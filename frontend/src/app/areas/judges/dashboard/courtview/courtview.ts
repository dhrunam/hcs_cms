import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { Router } from "@angular/router";
import { forkJoin, of } from "rxjs";
import { catchError } from "rxjs/operators";

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

interface CalendarDayCell {
  dateIso: string;
  dayNumber: number;
  isCurrentMonth: boolean;
  isSelected: boolean;
  isToday: boolean;
  hasCases: boolean;
  caseCount: number;
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
  monthCursor = this.parseIsoDate(this.forwardedForDate);
  readonly weekdayLabels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  listedCases: any[] = [];
  monthlyCaseCounts: Record<string, number> = {};

  constructor(
    private courtroomService: CourtroomService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.loadMonthAvailability();
    this.load();
  }

  onDateChange(): void {
    this.monthCursor = this.parseIsoDate(this.forwardedForDate);
    this.load();
  }

  get monthLabel(): string {
    return this.monthCursor.toLocaleDateString("en-IN", {
      month: "long",
      year: "numeric",
    });
  }

  get calendarCells(): CalendarDayCell[] {
    const year = this.monthCursor.getFullYear();
    const month = this.monthCursor.getMonth();
    const firstOfMonth = new Date(year, month, 1);
    const start = new Date(firstOfMonth);
    start.setDate(firstOfMonth.getDate() - firstOfMonth.getDay());

    const cells: CalendarDayCell[] = [];
    const todayIso = localCalendarDateIsoString();

    for (let i = 0; i < 42; i++) {
      const current = new Date(start);
      current.setDate(start.getDate() + i);
      const dateIso = this.toIsoDate(current);
      cells.push({
        dateIso,
        dayNumber: current.getDate(),
        isCurrentMonth: current.getMonth() === month,
        isSelected: dateIso === this.forwardedForDate,
        isToday: dateIso === todayIso,
        hasCases: (this.monthlyCaseCounts[dateIso] ?? 0) > 0,
        caseCount: this.monthlyCaseCounts[dateIso] ?? 0,
      });
    }

    return cells;
  }

  previousMonth(): void {
    this.monthCursor = new Date(
      this.monthCursor.getFullYear(),
      this.monthCursor.getMonth() - 1,
      1,
    );
    this.loadMonthAvailability();
  }

  nextMonth(): void {
    this.monthCursor = new Date(
      this.monthCursor.getFullYear(),
      this.monthCursor.getMonth() + 1,
      1,
    );
    this.loadMonthAvailability();
  }

  selectCalendarDate(dateIso: string): void {
    this.forwardedForDate = dateIso;
    this.monthCursor = this.parseIsoDate(dateIso);
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

  private parseIsoDate(dateIso: string): Date {
    const [year, month, day] = dateIso.split("-").map(Number);
    return new Date(year, (month || 1) - 1, day || 1);
  }

  private loadMonthAvailability(): void {
    const year = this.monthCursor.getFullYear();
    const month = this.monthCursor.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const requests: Record<string, ReturnType<CourtroomService["getPendingCases"]>> =
      {};

    for (let day = 1; day <= daysInMonth; day++) {
      const dateIso = this.toIsoDate(new Date(year, month, day));
      requests[dateIso] = this.courtroomService.getPendingCases(dateIso).pipe(
        catchError(() =>
          of({
            pending_for_listing: [],
            pending_for_causelist: [],
          }),
        ),
      );
    }

    forkJoin(requests).subscribe((results) => {
      const counts: Record<string, number> = {};
      Object.entries(results).forEach(([dateIso, resp]) => {
        const published = resp?.pending_for_causelist?.length ?? 0;
        const prePublish = resp?.pending_for_listing?.length ?? 0;
        counts[dateIso] = published + prePublish;
      });
      this.monthlyCaseCounts = counts;
    });
  }

  private toIsoDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }
}
