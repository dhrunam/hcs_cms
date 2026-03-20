import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { CaseTypeService } from '../../../../../../services/master/case-type.services';
import { OrganisationService } from '../../../../../../services/master/organisation.services';

@Component({
  selector: 'app-e-file',
  imports: [CommonModule],
  templateUrl: './e-file.html',
  styleUrl: './e-file.css',
})
export class EFile {
  @Input() form!: FormGroup;
  @Input() litigantList!: any;
  @Input() actList!: any;
  @Input() docList!: any;
  @Input() caseDetailsData: any;
  @Output() goToPage = new EventEmitter<number>();

  caseTypes: any[] = [];
  expandedRows: { [key: number]: boolean } = {};
  organisations: any[] = [];

  toggleRow(index: number) {
    this.expandedRows[index] = !this.expandedRows[index];
  }

  constructor(
    private caseTypeService: CaseTypeService,
    private organisationService: OrganisationService,
  ) {}

  ngOnInit() {
    this.get_case_types();
    this.get_organisation_list();
  }

  get_case_types() {
    this.caseTypeService.get_case_types().subscribe({
      next: (data) => {
        this.caseTypes = data.results;
      },
    });
  }

  get sortedLitigants() {
    return this.litigantList.sort(
      (a: any, b: any) => Number(b.is_petitioner) - Number(a.is_petitioner),
    );
  }

  get_case_type_name(id: number): string {
    return this.caseTypes.find((n) => n.id === id)?.name || '';
  }

  get_case_type_full_form(id: number): string {
    return this.caseTypes.find((n) => n.id === id)?.full_form || '';
  }

  get initialInputsForm(): FormGroup {
    return this.form.get('initialInputs') as FormGroup;
  }

  get litigantsForm(): FormGroup {
    return this.form.get('litigants') as FormGroup;
  }

  get caseDetailsForm(): FormGroup {
    return this.form.get('caseDetails') as FormGroup;
  }

  get caseDetailsView(): any {
    if (this.caseDetailsData) return this.caseDetailsData;
    return this.caseDetailsForm.getRawValue();
  }

  get_organisation_list() {
    this.organisationService.get_organisations().subscribe({
      next: (data) => {
        this.organisations = data.results;
        console.log(this.organisations);
      },
    });
  }

  get_organisation_name(id: number): string {
    return this.organisations.find((o) => o.id === id)?.orgname || '';
  }
  onUpdateClick(id: number) {
    this.goToPage.emit(id);
  }
}
