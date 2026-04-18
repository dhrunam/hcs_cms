import { CommonModule } from "@angular/common";
import { Component, Input, Output, EventEmitter } from "@angular/core";
import { FormGroup, FormsModule, ReactiveFormsModule } from "@angular/forms";
import { CaseTypeService } from "../../../../../../services/master/case-type.services";

@Component({
  selector: "app-initial-inputs",
  imports: [ReactiveFormsModule, CommonModule, FormsModule],
  templateUrl: "./initial-inputs.html",
  styleUrl: "./initial-inputs.css",
})
export class InitialInputs {
  constructor(private caseTypeService: CaseTypeService) {}

  @Input() form!: FormGroup;
  @Input() isDraft = false;
  @Input() isGovernmentBody = false;
  @Output() isGovernmentBodyChange = new EventEmitter<boolean>();
  case_types: any[] = [];

  ngOnInit() {
    this.get_case_types();
  }

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

  get_case_type_label(value: any): string {
    if (value?.type_name) return value.type_name;
    const id = value?.id ?? value;
    return (
      this.case_types.find((item) => Number(item.id) === Number(id))?.type_name ||
      ""
    );
  }
}
