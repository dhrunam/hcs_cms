import { CommonModule } from "@angular/common";
import {
  Component,
  EventEmitter,
  Input,
  Output,
  SimpleChanges,
} from "@angular/core";
import { FormGroup, ReactiveFormsModule } from "@angular/forms";
import { OrganisationService } from "../../../../../../services/master/organisation.services";
import { EfilingService } from "../../../../../../services/advocate/efiling/efiling.services";
import { StateAndDistrictService } from "../../../../../../services/master/state_and_district.services";

@Component({
  selector: "app-litigant",
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: "./litigant.html",
  styleUrl: "./litigant.css",
})
export class Litigant {
  @Input() petitionerForm!: FormGroup;
  @Input() respondentForm!: FormGroup;
  @Input() litigantList!: any;
  organisations: any[] = [];
  states: any[] = [];
  districts: any[] = [];
  @Output() deleted = new EventEmitter<number>();
  @Output() submitLitigant = new EventEmitter<"petitioner" | "respondent">();
  @Output() updateLitigant = new EventEmitter<"petitioner" | "respondent">();
  @Output() undoEdit = new EventEmitter<"petitioner" | "respondent">();
  @Output() startNew = new EventEmitter<"petitioner" | "respondent">();
  showPetitionerForm = true;
  showRespondentForm = true;

  constructor(
    private organisationService: OrganisationService,
    private eFilingService: EfilingService,
    private stateService: StateAndDistrictService,
  ) {}

  ngOnInit() {
    this.get_organisation_list();
    this.get_state_list();
    this.bindOrganisationToggle(this.petitionerForm);
    this.bindOrganisationToggle(this.respondentForm);
    this.bindOrganisationName(this.petitionerForm);
    this.bindOrganisationName(this.respondentForm);
    this.syncFormVisibility();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes["litigantList"]) {
      this.syncFormVisibility();
    }
  }

  startNewLitigant(side: "petitioner" | "respondent") {
    if (side === "petitioner") {
      this.showPetitionerForm = true;
    } else {
      this.showRespondentForm = true;
    }
    this.startNew.emit(side);
  }

  onSubmit(side: "petitioner" | "respondent", form: FormGroup) {
    if (this.isEditing(form)) {
      this.updateLitigant.emit(side);
      return;
    }

    this.submitLitigant.emit(side);
  }

  onUndo(side: "petitioner" | "respondent") {
    this.undoEdit.emit(side);
  }

  isEditing(form: FormGroup): boolean {
    return !!form?.get("id")?.value;
  }

  private bindOrganisationToggle(form: FormGroup) {
    const orgCtrl = form?.get("is_organisation");
    if (!orgCtrl) return;

    orgCtrl.valueChanges.subscribe((isOrg) => {
      if (isOrg) {
        form.patchValue({ gender: "", age: "" }, { emitEvent: false });
        return;
      }

      form.patchValue({ organization: "" }, { emitEvent: false });
    });
  }

  private bindOrganisationName(form: FormGroup) {
    const updateName = () => {
      const orgId = form.get("organization")?.value;
      const isOrg = form.get("is_organisation")?.value;
      const selectedOrg = this.organisations.find((o) => o.id == orgId);

      if (isOrg && orgId && selectedOrg) {
        form.get("name")?.setValue(selectedOrg.orgname);
      } else if (isOrg) {
        form.get("name")?.setValue("");
      }
    };

    form.get("organization")?.valueChanges.subscribe(updateName);
    form.get("is_organisation")?.valueChanges.subscribe(updateName);
  }

  delete_ligitant_details(id: number) {
    this.eFilingService.delete_litigant_details_by_id(id).subscribe({
      next: (data: any) => {
        this.deleted.emit(id);
      },
    });
  }

  editLitigant(item: any) {
    if (!item) return;

    const targetForm = this.isPetitioner(item.is_petitioner)
      ? this.petitionerForm
      : this.respondentForm;

    targetForm.patchValue({
      id: item.id ?? "",
      name: item.name ?? "",
      gender: item.gender ?? "",
      age: item.age ?? "",
      sequence_number: item.sequence_number ?? "",
      is_diffentially_abled: !!item.is_diffentially_abled,
      is_petitioner:
        item.is_petitioner === true ||
        item.is_petitioner === 1 ||
        item.is_petitioner === "1" ||
        item.is_petitioner === "true",
      is_organisation: item.organization !== null,
      organization:
        item.organization_detail?.id ??
        item.organization ??
        item.organization_id ??
        "",
      contact: item.contact ?? "",
      email: item.email ?? "",
      religion: item.religion ?? "",
      caste: item.caste ?? "",
      occupation: item.occupation ?? "",
      address: item.address ?? "",
      state_id: item.state_detail?.id ?? item.state_id ?? "",
      district_id: item.district_detail?.id ?? item.district_id ?? "",
      taluka: item.taluka ?? "",
      village: item.village ?? "",
    });

    const stateId = Number(item.state_detail?.id ?? item.state_id);
    if (stateId) {
      this.get_district_list_by_state_id(stateId);
    }
    // window.scrollTo({ top: 0, behavior: "smooth" });
  }

  get sortedLitigants() {
    return this.litigantList.sort(
      (a: any, b: any) => Number(b.is_petitioner) - Number(a.is_petitioner),
    );
  }

  private isPetitioner(value: any): boolean {
    return value === true || value === 1 || value === "1" || value === "true";
  }

  get petitionerLitigants() {
    const list = Array.isArray(this.litigantList) ? this.litigantList : [];
    return list.filter((item: any) => this.isPetitioner(item.is_petitioner));
  }

  get respondentLitigants() {
    const list = Array.isArray(this.litigantList) ? this.litigantList : [];
    return list.filter((item: any) => !this.isPetitioner(item.is_petitioner));
  }

  private syncFormVisibility() {
    const petitionerCount = this.petitionerLitigants.length;
    const respondentCount = this.respondentLitigants.length;
    this.showPetitionerForm = petitionerCount === 0;
    this.showRespondentForm = respondentCount === 0;
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

  onStateChange(event: any) {
    const stateId = event.target.value;

    if (stateId) {
      this.get_district_list_by_state_id(+stateId);
    }
  }

  get_district_list_by_state_id(state_id: number) {
    this.stateService.get_district_by_state_id(state_id).subscribe({
      next: (data) => {
        this.districts = Array.isArray(data?.results)
          ? data.results
          : data || [];
      },
    });
  }

  get_organisation_name(id: number): string {
    return this.organisations.find((o) => o.id === id)?.orgname || "";
  }

  deleteLitigant(id: number) {
    const confirmDelete = confirm(
      "Are you sure you want to delete this litigant?",
    );

    if (!confirmDelete) {
      return;
    }

    if (!id || Number(id) <= 0) {
      this.deleted.emit(id);
      return;
    }

    if (confirmDelete) {
      this.delete_ligitant_details(id);
    }
  }
}
