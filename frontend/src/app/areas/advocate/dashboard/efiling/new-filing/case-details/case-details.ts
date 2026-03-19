import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActService } from '../../../../../../services/master/acts.services';
import { Output, EventEmitter } from '@angular/core';
import { StateAndDistrictService } from '../../../../../../services/master/state_and_district.services';

@Component({
  selector: 'app-case-details',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './case-details.html',
  styleUrl: './case-details.css',
})
export class CaseDetails {
  @Input() form!: FormGroup;
  @Input() actList!: any;
  acts: any[] = [];
  states: any[] = [];
  districts: any[] = [];
  @Output() actListChange = new EventEmitter<any[]>();
  isDisabled = false;
  constructor(
    private actService: ActService,
    private stateService: StateAndDistrictService,
  ) {}

  ngOnInit() {
    this.get_act_types();
    this.get_state_list();
    this.isDisabled = this.form!.disabled;
  }

  get_state_list() {
    this.stateService.get_states().subscribe({
      next: (data) => {
        this.states = data.results;
      },
    });
  }
  get_districts(event:any){
    const stateId = parseInt(event.target.value);
    this.stateService.get_district_by_state_id(stateId).subscribe({
      next: (data) => {
        this.districts = data.results;
      },
    });
  }
  get_act_types() {
    this.actService.get_act_types().subscribe({
      next: (data) => {
        this.acts = data.results;
      },
    });
  }

  addAct(actInput?: any, sectionInput?: any) {
    let act, section;

    if (this.isDisabled) {
      act = actInput?.value;
      section = sectionInput?.value;
    } else {
      const group = this.form as FormGroup;
      act = group.get('act')?.value;
      section = group.get('section')?.value;
    }

    if (!act || !section) return;

    const selectedAct = this.acts.find((a: any) => a.actcode == act);

    this.actListChange.emit([
      {
        act,
        actname: selectedAct?.actname,
        section,
      },
    ]);

    if (this.isDisabled) {
      actInput.value = '';
      sectionInput.value = '';
    } else {
      const group = this.form as FormGroup;
      group.patchValue({ act: '', section: '' });
    }
  }
}
