import { CommonModule } from "@angular/common";
import { Component, Input } from "@angular/core";
import { FormGroup, ReactiveFormsModule } from "@angular/forms";
import { CaseTypeService } from "../../../../../../services/master/case-type.services";

@Component({
  selector: "app-initial-inputs",
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: "./initial-inputs.html",
  styleUrl: "./initial-inputs.css",
})
export class InitialInputs {
  // Wire services for case type lookups.
  constructor(private caseTypeService: CaseTypeService) {}

  @Input() form!: FormGroup;
  @Input() isDraft = false;
  case_types: any[] = [];

  // Load case type options for the select control.
  ngOnInit() {
    this.get_case_types();
  }

  // Fetch case types from API and normalize the response array.
  get_case_types() {
    this.caseTypeService.get_case_types().subscribe({
      next: (data) => {
        this.case_types = Array.isArray(data?.results)
          ? data.results
          : Array.isArray(data)
            ? data
            : [];
        console.log("Case type data is ", this.case_types);
      },
    });
  }

  // Resolve a case type label for draft/read-only display.
  get_case_type_label(value: any): string {
    if (value?.type_name) return value.type_name;
    const id = value?.id ?? value;
    return (
      this.case_types.find((item) => Number(item.id) === Number(id))?.type_name ||
      ""
    );
  }
}
