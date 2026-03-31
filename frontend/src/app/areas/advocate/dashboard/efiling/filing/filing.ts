import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { NewFiling } from "../new-filing/new-filing";
import { Create } from "../document-filing/create/create";
import { IaFilingForm } from "../ia-filing/filing-form/filing-form";

@Component({
  selector: "app-filing",
  standalone: true,
  imports: [CommonModule, NewFiling, Create, IaFilingForm],
  templateUrl: "./filing.html",
  styleUrl: "./filing.css",
})
export class Filing {
  activeTab: "new" | "existing" | "ia" = "new";

  setActive(tab: "new" | "existing" | "ia"): void {
    this.activeTab = tab;
  }
}

export default Filing;
