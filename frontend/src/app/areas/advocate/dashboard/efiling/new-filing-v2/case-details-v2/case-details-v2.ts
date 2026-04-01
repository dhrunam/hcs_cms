import { CommonModule } from "@angular/common";
import { FormGroup, ReactiveFormsModule } from "@angular/forms";
import { ActService } from "../../../../../../services/master/acts.services";
import { CaseTypeService } from "../../../../../../services/master/case-type.services";
import { OrganisationService } from "../../../../../../services/master/organisation.services";
import {
  Output,
  EventEmitter,
  Component,
  OnChanges,
  Input,
  SimpleChanges,
} from "@angular/core";
import { StateAndDistrictService } from "../../../../../../services/master/state_and_district.services";
import { formatPetitionerVsRespondent } from "../../../../../../utils/petitioner-vs-respondent";

@Component({
  selector: "app-case-details-v2",
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: "./case-details-v2.html",
  styleUrl: "./case-details-v2.css",
})
export class CaseDetailsV2 implements OnChanges {
  @Input() initialForm!: FormGroup;
  @Input() litigantForm!: FormGroup;
  @Input() caseDetailsForm!: FormGroup;
  @Input() litigantList: any[] = [];
  @Input() actList: any[] = [];
  @Input() isSaved = false;

  acts: any[] = [];
  caseTypes: any[] = [];
  organisations: any[] = [];
  states: any[] = [];
  litigantDistricts: any[] = [];
  disputeDistricts: any[] = [];

  @Output() addLitigant = new EventEmitter<void>();
  @Output() deleteLitigant = new EventEmitter<number>();
  @Output() actListChange = new EventEmitter<any[]>();
  @Output() actRemoved = new EventEmitter<number>();
  isCaseDetailsDisabled = false;

  constructor(
    private actService: ActService,
    private caseTypeService: CaseTypeService,
    private organisationService: OrganisationService,
    private stateService: StateAndDistrictService,
  ) {}

  ngOnInit() {
    this.get_case_types();
    this.get_organisation_list();
    this.get_act_types();
    this.get_state_list();
    this.bindOrganisationToggle();
    this.isCaseDetailsDisabled = this.caseDetailsForm?.disabled ?? false;
    this.caseDetailsForm?.statusChanges?.subscribe(() => {
      this.isCaseDetailsDisabled = this.caseDetailsForm?.disabled ?? false;
    });
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes["caseDetailsForm"]) {
      this.isCaseDetailsDisabled = this.caseDetailsForm?.disabled ?? false;
    }
  }

  private bindOrganisationToggle() {
    const orgCtrl = this.litigantForm?.get("is_organisation");
    if (!orgCtrl) return;

    orgCtrl.valueChanges.subscribe((isOrg) => {
      if (isOrg) {
        this.litigantForm.patchValue(
          { gender: "", age: "" },
          { emitEvent: false },
        );
        return;
      }

      this.litigantForm.patchValue({ organization: "" }, { emitEvent: false });
    });
  }

  get sortedLitigants() {
    return [...(this.litigantList || [])].sort(
      (a: any, b: any) => Number(b.is_petitioner) - Number(a.is_petitioner),
    );
  }

  get petitionerVsRespondentLine(): string {
    const pn = String(
      this.initialForm?.get("petitioner_name")?.value || "",
    ).trim();
    return formatPetitionerVsRespondent(this.litigantList, pn) || "—";
  }

  get hasRequiredLitigants(): boolean {
    const list = Array.isArray(this.litigantList) ? this.litigantList : [];
    const hasPetitioner = list.some((item) => item.is_petitioner);
    const hasRespondent = list.some((item) => !item.is_petitioner);
    return hasPetitioner && hasRespondent;
  }

  get_case_types() {
    this.caseTypeService.get_case_types().subscribe({
      next: (data) => {
        this.caseTypes = Array.isArray(data?.results)
          ? data.results
          : data || [];
      },
    });
  }

  get_organisation_list() {
    this.organisationService.get_organisations().subscribe({
      next: (data) => {
        this.organisations = Array.isArray(data?.results)
          ? data.results
          : data || [];
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

  onLitigantStateChange(event: any) {
    const stateId = parseInt(event.target.value);
    if (!stateId) {
      this.litigantDistricts = [];
      return;
    }
    this.stateService.get_district_by_state_id(stateId).subscribe({
      next: (data) => {
        this.litigantDistricts = Array.isArray(data?.results)
          ? data.results
          : data || [];
      },
    });
  }

  onDisputeStateChange(event: any) {
    const stateId = parseInt(event.target.value);
    if (!stateId) {
      this.disputeDistricts = [];
      return;
    }
    this.stateService.get_district_by_state_id(stateId).subscribe({
      next: (data) => {
        this.disputeDistricts = Array.isArray(data?.results)
          ? data.results
          : data || [];
      },
    });
  }

  get_act_types() {
    this.actService.get_act_types().subscribe({
      next: (data) => {
        this.acts = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
  }

  triggerAddLitigant() {
    this.addLitigant.emit();
  }

  triggerDeleteLitigant(id: number) {
    this.deleteLitigant.emit(id);
  }

  addAct(actInput?: any, sectionInput?: any) {
    let act, section;

    if (this.isCaseDetailsDisabled) {
      act = actInput?.value;
      section = sectionInput?.value;
    } else {
      const group = this.caseDetailsForm as FormGroup;
      act = group.get("act")?.value;
      section = group.get("section")?.value;
    }

    if (!act || !section) {
      const group = this.caseDetailsForm as FormGroup;
      group.get("act")?.markAsTouched();
      group.get("section")?.markAsTouched();
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

    if (this.isCaseDetailsDisabled) {
      actInput.value = "";
      sectionInput.value = "";
      return;
    }

    const group = this.caseDetailsForm as FormGroup;
    group.patchValue({ act: "", section: "" });
    group.get("act")?.markAsPristine();
    group.get("section")?.markAsPristine();
  }

  removeAct(index: number) {
    this.actRemoved.emit(index);
  }

  isControlInvalid(form: FormGroup, controlName: string): boolean {
    const control = form?.get(controlName);
    return !!control && control.invalid && (control.touched || control.dirty);
  }

  isActControlInvalid(controlName: string): boolean {
    if ((this.actList || []).length > 0) return false;
    return this.isControlInvalid(this.caseDetailsForm, controlName);
  }
}
