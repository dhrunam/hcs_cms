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
  acts: any[] = [];
  states: any[] = [];
  actList: any[] = [];
  @Output() actListChange = new EventEmitter<any[]>();
  constructor(
    private actService: ActService,
    private stateService: StateAndDistrictService,
  ) {}

  ngOnInit() {
    this.get_act_types();
    this.get_state_list();
  }

  get_state_list() {
    this.stateService.get_states().subscribe({
      next: (data) => {
        this.states = data.results;
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

  addAct() {
    const group = this.form as FormGroup;

    const act = group.get('act')?.value;
    const section = group.get('section')?.value;

    console.log('ACT:', act, 'SECTION:', section);

    const selectedAct = this.acts.find((a: any) => a.actcode == act);

    this.actList.push({
      act,
      actname: selectedAct?.actname,
      section,
    });

    this.actListChange.emit(this.actList);

    group.patchValue({
      act: null,
      section: '',
    });
  }
}
