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
  @Output() deleted = new EventEmitter<number>();
  constructor(
    private organisationService: OrganisationService,
    private eFilingService: EfilingService,
    private stateService: StateAndDistrictService,
  ) {}

  ngOnInit() {
    this.get_organisation_list();
    this.get_state_list();
  }

  delete_ligitant_details(id: number) {
    this.eFilingService.delete_litigant_details_by_id(id).subscribe({
      next: (data: any) => {
        this.deleted.emit(id);
      },
    });
  }

  get_organisation_list() {
    this.organisationService.get_organisations().subscribe({
      next: (data) => {
        this.organisations = data.results;
        console.log(this.organisations);
      },
    });
  }

  get_state_list() {
    this.stateService.get_states().subscribe({
      next: (data) => {
        this.states = data.results;
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
