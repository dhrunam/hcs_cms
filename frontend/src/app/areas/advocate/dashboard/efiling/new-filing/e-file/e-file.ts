import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { CaseTypeService } from '../../../../../../services/master/case-type.services';
import { OrganisationService } from '../../../../../../services/master/organisation.services';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
import { app_url } from '../../../../../../environment';

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
  @Input() paymentDetails: any;
  @Output() goToPage = new EventEmitter<number>();

  caseTypes: any[] = [];
  expandedRows: { [key: number]: boolean } = {};
  organisations: any[] = [];
  isMergingPdf = false;
  mergeError: string | null = null;

  toggleRow(index: number) {
    this.expandedRows[index] = !this.expandedRows[index];
  }

  constructor(
    private caseTypeService: CaseTypeService,
    private organisationService: OrganisationService,
    private efilingService: EfilingService,
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

  private normalizeIsPetitioner(value: any): boolean {
    return value === true || value === 'true' || value === 1 || value === '1';
  }

  private getOrderedPartyNames(isPetitioner: boolean): string[] {
    return (Array.isArray(this.litigantList) ? this.litigantList : [])
      .filter(
        (item: any) =>
          this.normalizeIsPetitioner(item?.is_petitioner) ===
          this.normalizeIsPetitioner(isPetitioner),
      )
      .sort(
        (a: any, b: any) =>
          (Number(a?.sequence_number) || 0) - (Number(b?.sequence_number) || 0),
      )
      .map((item: any) => String(item?.name || '').trim())
      .filter((name) => !!name);
  }

  private formatPartyForCoverPage(names: string[], fallback = ''): string {
    if (!names.length) return String(fallback || '').trim();
    if (names.length === 1) return names[0];
    if (names.length === 2) return `${names[0]} and Anr.`;
    return `${names[0]} and Ors.`;
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

  private resolveLocationLabel(value: any): string {
    if (!value) return '-';
    if (typeof value === 'string' || typeof value === 'number') return String(value);
    return value.state || value.district || value.name || value.label || value.title || '-';
  }

  getDisputeStateLabel(): string {
    return this.resolveLocationLabel(this.caseDetailsView?.state_detail?.state);
  }

  getDisputeDistrictLabel(): string {
    return this.resolveLocationLabel(this.caseDetailsView?.dispute_district);
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

  private getMergeItems(): { url: string; name: string }[] {
    const items: { url: string; name: string }[] = [];
    const list = Array.isArray(this.docList) ? this.docList : [];
    for (const doc of list) {
      const indexes = doc?.document_indexes;
      if (Array.isArray(indexes) && indexes.length > 0) {
        for (const part of indexes) {
          const url = part?.file_url || part?.file_part_path;
          if (url) {
            const name = part?.document_part_name?.trim() || doc?.document_type || 'Document';
            items.push({ url, name });
          }
        }
      } else if (doc?.final_document) {
        const url = doc.final_document;
        const name = doc?.document_type?.trim() || 'Document';
        items.push({ url, name });
      }
    }
    return items;
  }

  private toAbsoluteUrl(url: string): string {
    if (!url) return '';
    const s = String(url).trim();
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    const base = app_url.replace(/\/$/, '');
    return s.startsWith('/') ? `${base}${s}` : `${base}/${s}`;
  }

  canDownloadMerged(): boolean {
    return this.getMergeItems().length > 0;
  }

  downloadMergedPdf(): void {
    const items = this.getMergeItems();
    if (items.length === 0 || this.isMergingPdf) return;

    this.isMergingPdf = true;
    this.mergeError = null;

    const fetches = items.map((item) =>
      this.efilingService.fetch_document_blob(this.toAbsoluteUrl(item.url)),
    );

    forkJoin(fetches).subscribe({
      next: (blobs) => {
        const files = blobs.map((blob, i) => {
          const name = items[i].name.replace(/\.pdf$/i, '') + '.pdf';
          return new File([blob], name, { type: 'application/pdf' });
        });
        const names = items.map((i) => i.name);
        const petitioners = this.getOrderedPartyNames(true);
        const respondents = this.getOrderedPartyNames(false);
        const init = this.initialInputsView || {};
        const caseType = this.caseTypeFullForm || this.caseTypeLabel || '';
        const frontPage = {
          petitionerName: this.formatPartyForCoverPage(
            petitioners,
            (init.petitioner_name || '').trim(),
          ),
          respondentName: this.formatPartyForCoverPage(respondents, ''),
          caseNo: (init.e_filing_number || '').trim(),
          caseType,
        };

        this.efilingService.mergePdfs(files, names, frontPage).subscribe({
          next: (mergedBlob) => {
            const url = URL.createObjectURL(mergedBlob);
            const a = document.createElement('a');
            a.href = url;
            const docType = (this.docList?.[0]?.document_type || 'Documents').replace(/[^a-zA-Z0-9_-]/g, '_') || 'Documents';
            const efilingNo = (this.initialInputsView?.e_filing_number || '').replace(/[^a-zA-Z0-9_-]/g, '') || 'merged';
            a.download = `${docType}_${efilingNo}.pdf`;
            a.click();
            URL.revokeObjectURL(url);
            this.isMergingPdf = false;
          },
          error: (err) => {
            this.isMergingPdf = false;
            this.mergeError = err?.error?.error || err?.message || 'Failed to merge PDFs.';
          },
        });
      },
      error: () => {
        this.isMergingPdf = false;
        this.mergeError = 'Failed to fetch documents.';
      },
    });
  }
}
