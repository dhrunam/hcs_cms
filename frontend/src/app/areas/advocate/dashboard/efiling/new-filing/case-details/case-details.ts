import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
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
export class CaseDetails implements OnChanges {
  // Case details UI is currently hidden in New Filing template, kept for future re-enable.
  @Input() form!: FormGroup;
  @Input() actList!: any;
  acts: any[] = [];
  states: any[] = [];
  districts: any[] = [];
  @Output() actListChange = new EventEmitter<any[]>();
  @Output() actRemoved = new EventEmitter<number>();
  isDisabled = false;
  // Wire master data services for acts and geography lookups.
  constructor(
    private actService: ActService,
    private stateService: StateAndDistrictService,
  ) {}

  // Load initial act/state data and track disabled state.
  ngOnInit() {
    this.get_act_types();
    this.get_state_list();
    this.isDisabled = this.form!.disabled;
    this.form?.statusChanges?.subscribe(() => {
      this.isDisabled = this.form?.disabled ?? false;
    });
  }

  // Keep disabled flag in sync with input form changes.
  ngOnChanges(changes: SimpleChanges) {
    if (changes['form']) {
      this.isDisabled = this.form?.disabled ?? false;
    }
  }

  // Fetch states for the dispute location dropdown.
  get_state_list() {
    this.stateService.get_states().subscribe({
      next: (data) => {
        this.states = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
  }
  // Fetch districts for a selected state.
  get_districts(event: any) {
    const stateId = parseInt(event.target.value);
    this.stateService.get_district_by_state_id(stateId).subscribe({
      next: (data) => {
        this.districts = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
  }
  // Fetch acts for the act/section inputs.
  get_act_types() {
    this.actService.get_act_types().subscribe({
      next: (data) => {
        this.acts = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
  }

  // Add an act + section entry into the parent list and reset controls.
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

    if (!act || !section) {
      const group = this.form as FormGroup;
      group.get('act')?.markAsTouched();
      group.get('section')?.markAsTouched();
      return;
    }

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
      return;
    }

    const group = this.form as FormGroup;
    group.patchValue({ act: '', section: '' });
    group.get('act')?.markAsPristine();
    group.get('section')?.markAsPristine();
  }

  // Emit removal request for an act row.
  removeAct(index: number) {
    this.actRemoved.emit(index);
  }

  // Check if a control is invalid and has user interaction.
  isControlInvalid(controlName: string): boolean {
    const control = this.form?.get(controlName);
    return !!control && control.invalid && (control.touched || control.dirty);
  }

  // Validate act/section when no acts are already added.
  isActControlInvalid(controlName: string): boolean {
    if ((this.actList || []).length > 0) return false;
    return this.isControlInvalid(controlName);
  }
}
