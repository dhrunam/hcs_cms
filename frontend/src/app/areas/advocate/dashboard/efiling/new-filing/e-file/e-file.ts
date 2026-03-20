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
  @Input() filingData: any;
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
        this.caseTypes = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
  }

  get sortedLitigants() {
    return this.litigantList.sort(
      (a: any, b: any) => Number(b.is_petitioner) - Number(a.is_petitioner),
    );
  }

  get_case_type_name(id: number): string {
    const item = this.caseTypes.find((n) => n.id === id);
    return item?.type_name || item?.name || '';
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

  get initialInputsView(): any {
    return this.filingData || this.initialInputsForm.getRawValue();
  }

  private resolveCaseTypeFromValue(value: any): any | null {
    if (value && typeof value === 'object') return value;
    const id = Number(value);
    if (Number.isNaN(id)) return null;
    return this.caseTypes.find((item) => Number(item.id) === id) || null;
  }

  get caseTypeLabel(): string {
    const value = this.initialInputsView?.case_type;
    const resolved = this.resolveCaseTypeFromValue(value);
    return resolved?.type_name || resolved?.name || '';
  }

  get caseTypeFullForm(): string {
    const value = this.initialInputsView?.case_type;
    const resolved = this.resolveCaseTypeFromValue(value);
    return resolved?.full_form || '';
  }

  get caseDetailsView(): any {
    if (this.caseDetailsData) return this.caseDetailsData;
    return this.caseDetailsForm.getRawValue();
  }

  getActLabel(item: any): string {
    if (!item) return '-';
    if (item.actname) return item.actname;
    if (item.act_name) return item.act_name;
    if (item.act && typeof item.act === 'object') {
      return item.act.actname || item.act.act_name || item.act.act || '-';
    }
    if (item.act) return String(item.act);
    return '-';
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
