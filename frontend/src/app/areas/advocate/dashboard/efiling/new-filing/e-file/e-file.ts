import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { CaseTypeService } from '../../../../../../services/master/case-type.services';
import { OrganisationService } from '../../../../../../services/master/organisation.services';
import { EfilingService } from '../../../../../../services/advocate/efiling/efiling.services';
import { app_url } from '../../../../../../environment';
import {
  formatPartyLine,
  formatPetitionerVsRespondent,
  getOrderedPartyNames,
} from '../../../../../../utils/petitioner-vs-respondent';
import { jsPDF } from 'jspdf';

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
  /** Statutory court fee in rupees (e.g. WP(C) fee); optional, improves PDF court-fee line. */
  @Input() paymentFeeRupees: number | null = null;
  @Output() goToPage = new EventEmitter<number>();

  caseTypes: any[] = [];
  expandedRows: { [key: number]: boolean } = {};
  organisations: any[] = [];
  isMergingPdf = false;
  mergeError: string | null = null;

  // Toggle a litigant detail row in the preview table.
  toggleRow(index: number) {
    this.expandedRows[index] = !this.expandedRows[index];
  }

  // Wire lookup services used by preview labels and receipt metadata.
  constructor(
    private caseTypeService: CaseTypeService,
    private organisationService: OrganisationService,
    private efilingService: EfilingService,
  ) {}

  // Load case types and organisations for label resolution.
  ngOnInit() {
    this.get_case_types();
    this.get_organisation_list();
  }

  // Fetch case types from master data.
  get_case_types() {
    this.caseTypeService.get_case_types().subscribe({
      next: (data) => {
        this.caseTypes = Array.isArray(data?.results) ? data.results : data || [];
      },
    });
  }

  // Sort litigants with petitioners first for display.
  get sortedLitigants() {
    return this.litigantList.sort(
      (a: any, b: any) => Number(b.is_petitioner) - Number(a.is_petitioner),
    );
  }

  // Generate the petitioner vs respondent line for preview.
  get petitionerVsRespondentLine(): string {
    const init = this.initialInputsView || {};
    return (
      formatPetitionerVsRespondent(
        this.litigantList,
        String(init.petitioner_name || '').trim(),
      ) || '—'
    );
  }

  // Resolve case type name for a given id.
  get_case_type_name(id: number): string {
    const item = this.caseTypes.find((n) => n.id === id);
    return item?.type_name || item?.name || '';
  }

  // Resolve case type full form for a given id.
  get_case_type_full_form(id: number): string {
    return this.caseTypes.find((n) => n.id === id)?.full_form || '';
  }

  // Access initial inputs form group.
  get initialInputsForm(): FormGroup {
    return this.form.get('initialInputs') as FormGroup;
  }

  // Access litigants form group (unused when case-details step is hidden).
  get litigantsForm(): FormGroup {
    return this.form.get('litigants') as FormGroup;
  }

  // Access case details form group (case-details UI currently hidden).
  get caseDetailsForm(): FormGroup {
    return this.form.get('caseDetails') as FormGroup;
  }

  // Resolve initial inputs data from filing payload or form state.
  get initialInputsView(): any {
    return this.filingData || this.initialInputsForm.getRawValue();
  }

  // Normalize case type values that can be id or object.
  private resolveCaseTypeFromValue(value: any): any | null {
    if (value && typeof value === 'object') return value;
    const id = Number(value);
    if (Number.isNaN(id)) return null;
    return this.caseTypes.find((item) => Number(item.id) === id) || null;
  }

  // Case type label for preview.
  get caseTypeLabel(): string {
    const value = this.initialInputsView?.case_type;
    const resolved = this.resolveCaseTypeFromValue(value);
    return resolved?.type_name || resolved?.name || '';
  }

  // Case type full form for preview.
  get caseTypeFullForm(): string {
    const value = this.initialInputsView?.case_type;
    const resolved = this.resolveCaseTypeFromValue(value);
    return resolved?.full_form || '';
  }

  // Resolve case details from API payload or form state.
  get caseDetailsView(): any {
    if (this.caseDetailsData) return this.caseDetailsData;
    return this.caseDetailsForm.getRawValue();
  }

  // Normalize act label for mixed act payload shapes.
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

  // Normalize location values into a readable label.
  private resolveLocationLabel(value: any): string {
    if (!value) return '-';
    if (typeof value === 'string' || typeof value === 'number') return String(value);
    return value.state || value.district || value.name || value.label || value.title || '-';
  }

  // Resolve dispute state label.
  getDisputeStateLabel(): string {
    return this.resolveLocationLabel(this.caseDetailsView?.state_detail?.state);
  }

  // Resolve dispute district label.
  getDisputeDistrictLabel(): string {
    return this.resolveLocationLabel(this.caseDetailsView?.dispute_district);
  }

  // Fetch organisations list for label resolution.
  get_organisation_list() {
    this.organisationService.get_organisations().subscribe({
      next: (data) => {
        this.organisations = data.results;
        console.log(this.organisations);
      },
    });
  }

  // Resolve organisation name by id.
  get_organisation_name(id: number): string {
    return this.organisations.find((o) => o.id === id)?.orgname || '';
  }
  // Emit navigation event to return to an edit step.
  onUpdateClick(id: number) {
    this.goToPage.emit(id);
  }

  // Build list of document files to merge into a preview PDF.
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

  // Ensure document URLs are absolute for download/merge.
  private toAbsoluteUrl(url: string): string {
    if (!url) return '';
    const s = String(url).trim();
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    const base = app_url.replace(/\/$/, '');
    return s.startsWith('/') ? `${base}${s}` : `${base}/${s}`;
  }

  // True when an online receipt is eligible for download.
  get canDownloadOnlinePaymentReceipt(): boolean {
    const pd = this.paymentDetails;
    if (!pd || pd.required === false) return false;
    if (pd.outcome !== 'success') return false;
    const mode = String(pd.paymentMode || '').toLowerCase();
    return mode === 'online';
  }

  // Generate a PDF receipt for a successful online payment.
  downloadOnlinePaymentReceiptPdf(): void {
    if (!this.canDownloadOnlinePaymentReceipt) return;
    const pd = this.paymentDetails || {};
    const init = this.initialInputsView || {};
    const bench = String(init.bench || 'High Court Of Sikkim');
    const caseType = (this.caseTypeFullForm || this.caseTypeLabel || '-').trim() || '-';
    const eFilingNo = String(
      init.e_filing_number || this.filingData?.e_filing_number || '-',
    );
    const filingIdRaw = this.filingData?.id ?? this.filingData?.pk;
    const filingIdStr =
      filingIdRaw !== undefined && filingIdRaw !== null && filingIdRaw !== ''
        ? String(filingIdRaw)
        : '-';
    const amountStr = String(pd.courtFees || pd.amount || '').trim() || '-';
    const feeInput = this.paymentFeeRupees;
    const courtFeeStr =
      feeInput != null && Number.isFinite(feeInput) && feeInput > 0
        ? String(feeInput)
        : amountStr;
    const txnId = String(pd.txnId || '').trim() || '-';
    const referenceNo = String(pd.referenceNo || '').trim() || '-';
    const dateTimeLabel = this.formatPaymentReceiptDateTime(pd);

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 14;
    let y = 18;

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(16);
    doc.text('Court fee payment receipt', margin, y);
    y += 9;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(bench, margin, y);
    y += 11;

    const rows: [string, string][] = [
      ['E-filing number', eFilingNo],
      ['Application ID', filingIdStr],
      ['Case type', caseType],
      ['Payment purpose', 'Court fee (e-filing)'],
      ['Transaction ID', txnId],
      ['Reference number', referenceNo],
      ['Amount paid (INR)', `Rs. ${amountStr}/-`],
      ['Court fee (INR)', `Rs. ${courtFeeStr}/-`],
      ['Payment mode', 'Online'],
      ['Payment date / time', dateTimeLabel],
      ['Payment status', 'Successful'],
    ];

    doc.setFontSize(10);
    const labelX = margin;
    const valueX = margin + 52;
    const valueMaxW = pageWidth - valueX - margin;

    for (const [label, value] of rows) {
      doc.setFont('helvetica', 'bold');
      doc.text(`${label}:`, labelX, y);
      doc.setFont('helvetica', 'normal');
      const lines = doc.splitTextToSize(String(value), valueMaxW);
      doc.text(lines, valueX, y);
      y += Math.max(6, lines.length * 5.5) + 2;
    }

    y += 6;
    doc.setFontSize(9);
    doc.setTextColor(90);
    const footer = `Generated on ${new Date().toLocaleString()}. This document is a record of your online court fee payment.`;
    doc.text(doc.splitTextToSize(footer, pageWidth - margin * 2), margin, y);
    doc.setTextColor(0);

    const safeEf = (eFilingNo !== '-' ? eFilingNo : `filing-${filingIdStr}`).replace(
      /[^\w.-]+/g,
      '_',
    );
    const safeTxn = (pd.txnId ? String(pd.txnId) : 'receipt')
      .replace(/[^\w.-]+/g, '_')
      .slice(0, 48);
    doc.save(`payment-receipt-${safeEf}-${safeTxn}.pdf`);
  }

  private formatPaymentReceiptDateTime(pd: Record<string, unknown>): string {
  // Format payment date/time for receipt output.
    const raw = (pd['paidAt'] || pd['paymentDate']) as string | undefined;
    if (!raw || String(raw).trim() === '') return '-';
    const d = new Date(raw);
    if (!Number.isNaN(d.getTime())) return d.toLocaleString();
    return String(raw);
  }

  canDownloadMerged(): boolean {
  // Check if merge button should be enabled.
    return this.getMergeItems().length > 0;
  }

  // Merge uploaded document parts and download a single PDF.
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
        const init = this.initialInputsView || {};
        const petitioners = getOrderedPartyNames(this.litigantList, true);
        const respondents = getOrderedPartyNames(this.litigantList, false);
        const caseType = this.caseTypeFullForm || this.caseTypeLabel || '';
        const frontPage = {
          petitionerName:
            formatPartyLine(petitioners) ||
            String(init.petitioner_name || '').trim(),
          respondentName: formatPartyLine(respondents),
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
