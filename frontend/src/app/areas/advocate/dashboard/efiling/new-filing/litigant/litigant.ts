import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { OrganisationService } from '../../../../../../services/master/organisation.services';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
import { StateAndDistrictService } from '../../../../../../services/master/state_and_district.services';

@Component({
  selector: 'app-litigant',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './litigant.html',
  styleUrl: './litigant.css',
})
export class Litigant {
  @Input() form!: FormGroup;
  @Input() litigantList!: any;
  organisations: any[] = [];
  states: any[] = [];
  districts: any[] = [];
  @Output() deleted = new EventEmitter<number>();
  expandedRows: { [key: number]: boolean } = {};

  toggleRow(index: number) {
    this.expandedRows[index] = !this.expandedRows[index];
  }
  constructor(
    private organisationService: OrganisationService,
    private eFilingService: EfilingService,
    private stateService: StateAndDistrictService,
  ) {}

  ngOnInit() {
    this.get_organisation_list();
    this.get_state_list();
    this.bindOrganisationToggle();
  }

  private bindOrganisationToggle() {
    const orgCtrl = this.form?.get('is_organisation');
    if (!orgCtrl) return;

    orgCtrl.valueChanges.subscribe((isOrg) => {
      if (isOrg) {
        this.form.patchValue({ gender: '', age: '' }, { emitEvent: false });
        return;
      }

      this.form.patchValue({ organization: '' }, { emitEvent: false });
    });
  }

  delete_ligitant_details(id: number) {
    this.eFilingService.delete_litigant_details_by_id(id).subscribe({
      next: (data: any) => {
        this.deleted.emit(id);
      },
    });
  }

  get sortedLitigants() {
    return this.litigantList.sort(
      (a: any, b: any) => Number(b.is_petitioner) - Number(a.is_petitioner),
    );
  }

  get hasRequiredLitigants(): boolean {
    const list = Array.isArray(this.litigantList) ? this.litigantList : [];
    const hasPetitioner = list.some((item) => item.is_petitioner);
    const hasRespondent = list.some((item) => !item.is_petitioner);
    return hasPetitioner && hasRespondent;
  }

  get_organisation_list() {
    this.organisationService.get_organisations().subscribe({
      next: (data) => {
        this.organisations = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
  }

  get_state_list() {
    this.stateService.get_states().subscribe({
      next: (data) => {
        this.states = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
  }

  onStateChange(event: any) {
    const stateId = event.target.value;

    if (stateId) {
      this.get_district_list_by_state_id(+stateId);
    }
  }

  get_district_list_by_state_id(state_id: number) {
    this.stateService.get_district_by_state_id(state_id).subscribe({
      next: (data) => {
        this.districts = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
  }

  get_organisation_name(id: number): string {
    return this.organisations.find((o) => o.id === id)?.orgname || '';
  }

  deleteLitigant(id: number) {
    const confirmDelete = confirm('Are you sure you want to delete this litigant?');

    if (confirmDelete) {
      this.delete_ligitant_details(id);
    }
  }
}
