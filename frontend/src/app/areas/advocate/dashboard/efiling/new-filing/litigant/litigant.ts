import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { OrganisationService } from '../../../../../../services/master/organisation.services';

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
  constructor(private organisationService: OrganisationService) {}

  ngOnInit() {
    this.get_organisation_list();
  }

  get_organisation_list() {
    this.organisationService.get_organisations().subscribe({
      next: (data) => {
        this.organisations = data.results;
      },
    });
  }
}
