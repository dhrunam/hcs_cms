import { CommonModule } from "@angular/common";
import {
  ChangeDetectorRef,
  Component,
  EventEmitter,
  Input,
  NgZone,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
} from "@angular/core";
import { FormGroup, FormsModule, ReactiveFormsModule } from "@angular/forms";
import { ToastrService } from "ngx-toastr";
import { EfilingService } from "../../../../../../services/advocate/efiling/efiling.services";
import { validatePdfFiles } from "../../../../../../utils/pdf-validation";
import {
  CdkDragDrop,
  DragDropModule,
  moveItemInArray,
} from "@angular/cdk/drag-drop";
import { docTypes } from "../../../../../../utils/doc-types.const";
import { isFrontendManagedAnnexureDocumentIndexName } from "../../../../../../utils/efiling-new-filing-document-index";

interface DocumentUploadEntry {
  file: File;
  index_name: string;
  index_id: number | null;
  is_annexure?: boolean;
}

interface DocumentIndexMaster {
  id: number;
  name: string;
}

interface DocTypeOption {
  case_type_id: number;
  code: string;
  documents: string[];
}

interface UploadDocumentsPayloadItem {
  file: File;
  index_name: string;
  index_id: number | null;
}

interface UploadDocumentsPayload {
  document_type: string;
  /** When set, a header row is created first (no file); file rows link via parent_document_index. */
  parent_group_name?: string;
  items: UploadDocumentsPayloadItem[];
}

interface StructuredIndexRow {
  index_name: string;
  index_id: number | null;
  file: File | null;
}

const MEMO_OF_APPEAL_DOCUMENT_TYPE = "Memo of Appeal";
const MEMO_OF_APPEAL_INDEX_NAME = "Memo of Appeal";

@Component({
  selector: "app-upload-documents",
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, DragDropModule],
  templateUrl: "./upload-documents.html",
  styleUrl: "./upload-documents.css",
})
export class UploadDocuments implements OnInit, OnChanges {
  @Output() submitDoc = new EventEmitter<UploadDocumentsPayload>();
  @Input() form!: FormGroup;
  @Input() isUploading = false;
  @Input() fileProgresses: number[] = [];
  @Input() uploadCompletedToken = 0;
  /** When set, hides the document type field and uses this value (e.g. 'IA' for IA filing). */
  @Input() defaultDocumentType: string | null = null;
  /** Optional front page data for merged PDF (petitioner vs respondent, case no, case type). */
  @Input() frontPage: {
    petitionerName: string;
    respondentName: string;
    caseNo: string;
    caseType?: string;
  } | null = null;
  /** E-Filing number for merged PDF filename (e.g. DocumentType_efilingno.pdf). */
  @Input() eFilingNumber: string | null = null;
  /** Case type id for filtering index name options. */
  @Input() caseTypeId: number | null = null;
  /**
   * Rows from GET document-index/?case_type=&for_new_filing=true (ids + names).
   * When provided, replaces the unfiltered document-index master fetch.
   */
  @Input() documentIndexMasterList: Array<{ id: number; name: string }> = [];
  /** Index names already uploaded for this filing (avoid duplicates). */
  @Input() existingIndexNames: string[] = [];
  /** Enforce and auto-sequence mandatory indexes (e.g. WP(C) Main Petition). */
  @Input() mandatoryIndexNames: string[] = [];
  /** Enables sequential annexures (Annexure P1, P2, … by default). */
  @Input() enableAnnexureSequence = false;
  /** Letter after "Annexure " before the sequence number: P (petitioner), A (appellant), R (respondent). */
  @Input() annexureSequenceLetter: "P" | "A" | "R" = "P";
  /**
   * After which mandatory row (0-based) the Annexure(s) row appears; `-1` = before all.
   * From API sequence when parent provides it; otherwise the component falls back to Vakalatnama/last row.
   */
  @Input() annexureUiInsertAfterRowIndex?: number;
  /** Render fixed index rows with per-row upload controls. */
  @Input() structuredIndexUpload = false;
  /** Use free-text input for index name instead of dropdown. */
  @Input() useTextIndexName = false;
  /**
   * With useTextIndexName: require a top-level "Name" for the parent index row (no file),
   * then upload indexes/annexures as children linked in the database.
   */
  @Input() useParentIndexGroup = false;
  /**
   * With useTextIndexName + useParentIndexGroup: show multiple Index + PDF rows
   * and "Add index" instead of a single staged row + annexures.
   */
  @Input() multiManualIndexRows = false;
  /** Optional memo-of-appeal upload (separate document type); does not affect mandatory indexes. */
  @Input() enableMemoOfAppeal = false;
  /** When true, main filing already has a "Memo of Appeal" document — hide duplicate upload. */
  @Input() memoAlreadyUploaded = false;
  stagedIndexName = "";
  stagedFile: File | null = null;
  /** Parent EfilingDocumentsIndex.document_part_name (header row, no file) when useParentIndexGroup. */
  parentGroupName = "";
  /** Per-row manual index + file when {@link multiManualIndexRows} is true. */
  manualIndexRows: Array<{ id: number; indexName: string; file: File | null }> =
    [{ id: 1, indexName: "", file: null }];
  private nextManualRowId = 2;
  memoAppealFile: File | null = null;

  entries: DocumentUploadEntry[] = [];
  indexMasters: DocumentIndexMaster[] = [];
  submitAttempted = false;
  isSubmitting = false;
  isMerging = false;
  mergeError: string | null = null;
  private annexureCounter = 1;
  private mandatoryIndexCursor = 0;
  structuredRows: StructuredIndexRow[] = [];
  annexureRows: StructuredIndexRow[] = [];

  constructor(
    private eFilingService: EfilingService,
    private toastr: ToastrService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone,
  ) {}

  ngOnInit(): void {
    const initialDocType = this.getEffectiveDocumentType();
    if (initialDocType) {
      this.form?.patchValue({ document_type: initialDocType });
    }
    this.syncDocumentIndexMasters();
    this.ensureIndexMastersForMatching();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes["defaultDocumentType"]) {
      const value = this.getEffectiveDocumentType();
      if (value) {
        this.form?.patchValue({ document_type: value });
      }
    }
    if (
      changes["uploadCompletedToken"] &&
      !changes["uploadCompletedToken"].firstChange
    ) {
      this.form.reset();
      this.isSubmitting = false;
      const value = this.getEffectiveDocumentType();
      if (value) {
        this.form?.patchValue({ document_type: value });
      }
      this.entries = [];
      this.annexureCounter = 1;
      this.annexureRows = [];
      this.memoAppealFile = null;
      this.parentGroupName = "";
      this.manualIndexRows = [{ id: 1, indexName: "", file: null }];
      this.nextManualRowId = 2;
      this.initializeStructuredRows();
    }
    if (
      changes["mandatoryIndexNames"] ||
      changes["structuredIndexUpload"] ||
      changes["caseTypeId"]
    ) {
      const mandatoryNamesReallyChanged =
        !!changes["mandatoryIndexNames"] &&
        !changes["mandatoryIndexNames"].firstChange &&
        !this.sameStringArray(
          changes["mandatoryIndexNames"].previousValue,
          changes["mandatoryIndexNames"].currentValue,
        );
      if (
        mandatoryNamesReallyChanged ||
        (changes["caseTypeId"] && !changes["caseTypeId"].firstChange) ||
        (changes["structuredIndexUpload"] &&
          !changes["structuredIndexUpload"].firstChange)
      ) {
        this.annexureRows = [];
      }
      this.ensureIndexMastersForMatching();
    }
    if (changes["documentIndexMasterList"]) {
      this.syncDocumentIndexMasters();
      this.ensureIndexMastersForMatching();
    }
    if (
      changes["annexureSequenceLetter"] &&
      !changes["annexureSequenceLetter"].firstChange
    ) {
      this.renameAnnexuresToCurrentLetter();
      this.syncAnnexureCounterForCurrentLetter();
      this.cdr.markForCheck();
    }
  }

  /** Annexure P1 / A2 / R3 … auto-generated index names. */
  private static readonly ANNEXURE_AUTO_NAME_RE =
    /^annexure\s+([arp])\s*(\d+)\s*$/i;

  private annexureRenamedName(
    indexName: string,
    letter: "P" | "A" | "R",
  ): string | null {
    const m = String(indexName || "")
      .trim()
      .match(UploadDocuments.ANNEXURE_AUTO_NAME_RE);
    if (!m) return null;
    return `Annexure ${letter}${m[2]}`;
  }

  private resolveIndexIdForAnnexureName(name: string): number | null {
    const matchedMaster = this.indexMasters.find(
      (item) => item.name.toLowerCase() === String(name || "").toLowerCase(),
    );
    return matchedMaster ? matchedMaster.id : null;
  }

  /**
   * When litigant type changes, restage annexure labels to the new P/A/R letter
   * while keeping numeric suffixes.
   */
  private renameAnnexuresToCurrentLetter(): void {
    const letter = this.getAnnexureLetter();

    if (this.annexureRows.length > 0) {
      this.annexureRows = this.annexureRows.map((row) => {
        const newName = this.annexureRenamedName(row.index_name, letter);
        if (!newName) return row;
        return {
          ...row,
          index_name: newName,
          index_id: this.resolveIndexIdForAnnexureName(newName),
        };
      });
    }

    if (this.entries.some((e) => e.is_annexure)) {
      this.entries = this.entries.map((entry) => {
        if (!entry.is_annexure) return entry;
        const newName = this.annexureRenamedName(entry.index_name, letter);
        if (!newName) return entry;
        return {
          ...entry,
          index_name: newName,
          index_id: this.resolveIndexIdForAnnexureName(newName),
        };
      });
    }
  }

  private getAnnexureLetter(): "P" | "A" | "R" {
    const c = String(this.annexureSequenceLetter ?? "P")
      .trim()
      .toUpperCase();
    if (c === "A" || c === "R" || c === "P") return c;
    return "P";
  }

  /** Next annexure index name for the current letter; flat annexures only. */
  private maxFlatAnnexureSuffixForLetter(letter: string): number {
    let max = 0;
    const L = letter.toUpperCase();
    const re = /^annexure\s+([arp])\s*(\d+)\s*$/i;
    for (const e of this.getAnnexureEntries()) {
      const m = String(e.index_name || "").trim().match(re);
      if (m && m[1].toUpperCase() === L) {
        const n = parseInt(m[2], 10);
        if (Number.isFinite(n)) max = Math.max(max, n);
      }
    }
    return max;
  }

  private syncAnnexureCounterForCurrentLetter(): void {
    const L = this.getAnnexureLetter();
    const flatMax = this.maxFlatAnnexureSuffixForLetter(L);
    const structMax = this.maxAnnexureNameSuffix(this.annexureRows, L);
    this.annexureCounter = Math.max(flatMax, structMax) + 1;
  }

  /**
   * Prefer parent-provided documentIndexMasterList; if missing but structured
   * uploads need index_id, fetch filtered API then fall back to full master.
   */
  private ensureIndexMastersForMatching(): void {
    const structuredFinish = () => {
      this.initializeStructuredRows();
      this.cdr.markForCheck();
    };

    if (this.isStructuredMode()) {
      // Rows must exist before async index masters return (empty array breaks
      // hasUploadedAllStructuredDocuments because [].every(...) is true).
      this.initializeStructuredRows();
      if (this.indexMasters.length > 0) {
        return;
      }
      if (!this.mandatoryIndexNames?.length || !this.caseTypeId) {
        return;
      }
      this.fetchCaseTypeDocumentIndexes(structuredFinish);
      return;
    }

    if (this.indexMasters.length > 0) {
      return;
    }
    if (!this.caseTypeId) {
      return;
    }
    this.fetchCaseTypeDocumentIndexes(() => this.cdr.markForCheck());
  }

  private fetchCaseTypeDocumentIndexes(done: () => void): void {
    if (!this.caseTypeId) {
      done();
      return;
    }
    this.eFilingService
      .get_document_index_for_new_filing(this.caseTypeId)
      .subscribe({
        next: (res) => {
          const rows = Array.isArray(res)
            ? res
            : Array.isArray(res?.results)
              ? res.results
              : [];
          this.indexMasters = rows
            .map((item: any) => ({
              id: Number(item?.id),
              name: String(item?.name ?? "").trim(),
            }))
            .filter(
              (item: DocumentIndexMaster) =>
                Number.isFinite(item.id) &&
                !!item.name &&
                !isFrontendManagedAnnexureDocumentIndexName(item.name),
            );
          if (this.indexMasters.length === 0) {
            this.loadFullIndexMasterForMatching(done);
          } else {
            done();
          }
        },
        error: () => this.loadFullIndexMasterForMatching(done),
      });
  }

  private loadFullIndexMasterForMatching(done: () => void): void {
    this.eFilingService.get_document_index_master().subscribe({
      next: (r2) => {
        const all = Array.isArray(r2)
          ? r2
          : Array.isArray(r2?.results)
            ? r2.results
            : [];
        this.indexMasters = all
          .map((item: any) => ({
            id: Number(item?.id),
            name: String(item?.name ?? "").trim(),
          }))
          .filter(
            (item: DocumentIndexMaster) =>
              Number.isFinite(item.id) &&
              !!item.name &&
              !isFrontendManagedAnnexureDocumentIndexName(item.name),
          );
        done();
      },
      error: () => done(),
    });
  }

  private syncDocumentIndexMasters(): void {
    const rows = Array.isArray(this.documentIndexMasterList)
      ? this.documentIndexMasterList
      : [];
    this.indexMasters = rows
      .map((item: any) => ({
        id: Number(item?.id),
        name: String(item?.name ?? "").trim(),
      }))
      .filter(
        (item: DocumentIndexMaster) =>
          Number.isFinite(item.id) &&
          !!item.name &&
          !isFrontendManagedAnnexureDocumentIndexName(item.name),
      );
  }

  private isStructuredMode(): boolean {
    return this.structuredIndexUpload && this.mandatoryIndexNames.length > 0;
  }

  /** Parent may pass a new array reference each CD (e.g. getter + .map()); compare by value. */
  private sameStringArray(prev: unknown, curr: unknown): boolean {
    const a = prev as string[] | undefined;
    const b = curr as string[] | undefined;
    if (!Array.isArray(a) || !Array.isArray(b)) return false;
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i += 1) {
      if (String(a[i]) !== String(b[i])) return false;
    }
    return true;
  }

  private initializeStructuredRows() {
    if (!this.isStructuredMode()) return;
    const prevByName = new Map<string, StructuredIndexRow>();
    const prevById = new Map<number, StructuredIndexRow>();
    for (const r of this.structuredRows) {
      const nk = String(r.index_name).trim().toLowerCase();
      if (nk) prevByName.set(nk, r);
      const rid = r.index_id;
      if (rid != null && Number.isFinite(Number(rid))) {
        prevById.set(Number(rid), r);
      }
    }
    const baseRows = this.mandatoryIndexNames
      .filter((name) => !isFrontendManagedAnnexureDocumentIndexName(name))
      .map((name) => {
        const clean = String(name).trim();
        const key = clean.toLowerCase();
        const matchedMaster = this.indexMasters.find(
          (item) => item.name.toLowerCase() === key,
        );
        const mid = matchedMaster?.id;
        const byId =
          mid != null && Number.isFinite(mid) ? prevById.get(mid) : undefined;
        const prev = byId ?? prevByName.get(key);
        return {
          index_name: clean,
          index_id: mid ?? prev?.index_id ?? null,
          file: prev?.file ?? null,
        } as StructuredIndexRow;
      });
    this.structuredRows = baseRows;
    this.syncStructuredFinalDocument();
    this.cdr.markForCheck();
  }

  onTopDocumentTypeInput(value: string) {
    this.form.patchValue({ document_type: value });
  }

  isDocumentTypeInvalid(): boolean {
    const control = this.form?.get("document_type");
    return !!control && control.invalid && (control.touched || control.dirty);
  }

  isFilesInvalid(): boolean {
    return this.submitAttempted && this.entries.length === 0;
  }

  onFileChange(event: Event) {
    if (this.isStructuredMode()) return;
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const files = Array.from(input.files);
    const { valid, errors } = validatePdfFiles(files);
    if (errors.length > 0) {
      this.toastr.error(errors.join(" "));
    }
    if (valid.length === 0) return;

    const selectedEntries: DocumentUploadEntry[] = valid.map((file) => {
      const indexName = this.getAutoIndexName();
      const matchedMaster = this.indexMasters.find(
        (item) => item.name.toLowerCase() === indexName.toLowerCase(),
      );
      return {
        file,
        index_name: indexName,
        index_id: matchedMaster ? matchedMaster.id : null,
        is_annexure: false,
      };
    });

    this.entries = [...this.entries, ...selectedEntries];

    const currentDocType = this.getEffectiveDocumentType();
    if (currentDocType) {
      this.form?.patchValue({ document_type: currentDocType });
    }

    this.form.patchValue({
      final_document: this.entries.length > 0 ? this.entries[0].file : null,
    });

    input.value = "";
    this.cdr.markForCheck();
    this.cdr.detectChanges();
  }

  onStagedFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] || null;
    if (!file) return;
    const { valid, errors } = validatePdfFiles([file]);
    if (errors.length > 0) {
      this.toastr.error(errors.join(" "));
      input.value = "";
      return;
    }
    this.stagedFile = valid[0] || null;
    input.value = "";
    this.cdr.markForCheck();
    this.cdr.detectChanges();
  }

  clearStagedFile() {
    this.stagedFile = null;
  }

  trackByManualRowId(
    _: number,
    row: { id: number; indexName: string; file: File | null },
  ): number {
    return row.id;
  }

  addManualIndexRow(): void {
    if (this.isUploading) return;
    this.manualIndexRows = [
      ...this.manualIndexRows,
      { id: this.nextManualRowId++, indexName: "", file: null },
    ];
    this.cdr.markForCheck();
  }

  removeManualIndexRow(rowId: number): void {
    if (this.isUploading || this.manualIndexRows.length <= 1) return;
    this.manualIndexRows = this.manualIndexRows.filter((r) => r.id !== rowId);
    this.cdr.markForCheck();
  }

  onManualRowFileChange(
    row: { id: number; indexName: string; file: File | null },
    event: Event,
  ): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] || null;
    if (!file) return;
    const { valid, errors } = validatePdfFiles([file]);
    if (errors.length > 0) {
      this.toastr.error(errors.join(" "));
      input.value = "";
      return;
    }
    const picked = valid[0] || null;
    this.manualIndexRows = this.manualIndexRows.map((r) =>
      r.id === row.id ? { ...r, file: picked } : r,
    );
    input.value = "";
    this.cdr.markForCheck();
  }

  clearManualRowFile(row: { id: number; indexName: string; file: File | null }): void {
    this.manualIndexRows = this.manualIndexRows.map((r) =>
      r.id === row.id ? { ...r, file: null } : r,
    );
    this.cdr.markForCheck();
  }

  onStructuredFileChange(rowIndex: number, event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;
    const file = input.files[0];
    const { valid, errors } = validatePdfFiles([file]);
    if (errors.length > 0) {
      this.toastr.error(errors.join(" "));
      input.value = "";
      return;
    }
    const picked = valid[0];
    if (!picked || rowIndex < 0 || rowIndex >= this.structuredRows.length) {
      input.value = "";
      return;
    }
    this.structuredRows = this.structuredRows.map((r, i) =>
      i === rowIndex ? { ...r, file: picked } : r,
    );
    this.syncStructuredFinalDocument();
    input.value = "";
    this.cdr.markForCheck();
    this.cdr.detectChanges();
  }

  /**
   * "Add Annexures" opens the file dialog; each chosen PDF becomes a row
   * Annexure {P|A|R}1, … in order for the active annexureSequenceLetter.
   */
  onStructuredAnnexureFilesPicked(event: Event): void {
    if (this.isUploading) return;
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;
    const files = Array.from(input.files);
    const { valid, errors } = validatePdfFiles(files);
    if (errors.length > 0) {
      this.toastr.error(errors.join(" "));
    }
    if (valid.length === 0) {
      input.value = "";
      return;
    }
    const letter = this.getAnnexureLetter();
    let n = this.getNextAnnexureSequenceNumber();
    const additions: StructuredIndexRow[] = valid.map((file) => {
      const name = `Annexure ${letter}${n++}`;
      const matchedMaster = this.indexMasters.find(
        (item) => item.name.toLowerCase() === name.toLowerCase(),
      );
      return {
        index_name: name,
        index_id: matchedMaster ? matchedMaster.id : null,
        file,
      };
    });
    this.annexureRows = [...this.annexureRows, ...additions];
    this.syncStructuredFinalDocument();
    input.value = "";
    this.cdr.markForCheck();
    this.cdr.detectChanges();
  }

  private getNextAnnexureSequenceNumber(): number {
    const L = this.getAnnexureLetter();
    const fromNames = this.maxAnnexureNameSuffix(this.annexureRows, L);
    const countForLetter = this.annexureRows.filter((r) => {
      const m = String(r.index_name || "").trim().match(/^annexure\s+([arp])\s*\d+\s*$/i);
      return m && m[1].toUpperCase() === L;
    }).length;
    return Math.max(fromNames, countForLetter) + 1;
  }

  private maxAnnexureNameSuffix(
    rows: StructuredIndexRow[],
    letter: string,
  ): number {
    let max = 0;
    const L = letter.toUpperCase();
    const re = /^annexure\s+([arp])\s*(\d+)\s*$/i;
    for (const r of rows) {
      const m = String(r.index_name || "").trim().match(re);
      if (m && m[1].toUpperCase() === L) {
        const n = parseInt(m[2], 10);
        if (Number.isFinite(n)) max = Math.max(max, n);
      }
    }
    return max;
  }

  removeAnnexureRow(index: number) {
    this.annexureRows = this.annexureRows.filter((_, i) => i !== index);
    this.syncStructuredFinalDocument();
    this.cdr.markForCheck();
    this.cdr.detectChanges();
  }

  clearStructuredRowFile(index: number) {
    if (index < 0 || index >= this.structuredRows.length) return;
    this.structuredRows = this.structuredRows.map((r, i) =>
      i === index ? { ...r, file: null } : r,
    );
    this.syncStructuredFinalDocument();
    this.cdr.markForCheck();
    this.cdr.detectChanges();
  }

  previewLocalFile(file: File | null) {
    if (!file) return;
    const url = URL.createObjectURL(file);
    window.open(url, "_blank");
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }

  getStructuredCompletedCount(): number {
    const mandatoryFilled = this.structuredRows.filter((row) => !!row.file).length;
    const annexureFilled = this.enableAnnexureSequence
      ? this.annexureRows.length > 0
        ? 1
        : 0
      : 0;
    return mandatoryFilled + annexureFilled;
  }

  getStructuredTotalCount(): number {
    return this.structuredRows.length + (this.enableAnnexureSequence ? 1 : 0);
  }

  getStructuredCompletionPercent(): number {
    const total = this.getStructuredTotalCount();
    if (!total) return 0;
    return Math.round((this.getStructuredCompletedCount() / total) * 100);
  }

  private getVakalatnamaIndex(): number {
    return this.structuredRows.findIndex(
      (row) => row.index_name.trim().toLowerCase() === "vakalatnama",
    );
  }

  /** Stabilizes *ngFor when `mandatoryIndexNames` / API data refreshes. */
  trackByStructuredRow(_index: number, row: StructuredIndexRow): string {
    const id = row.index_id;
    if (id != null && Number.isFinite(id)) {
      return `id:${id}`;
    }
    return `name:${String(row.index_name || "").toLowerCase()}`;
  }

  trackByAnnexureRow(index: number, row: StructuredIndexRow): string {
    const f = row.file;
    const fp =
      f != null
        ? `${f.name}:${f.size}:${f.lastModified}`
        : "nofile";
    return `${row.index_name}:${fp}:${index}`;
  }

  /** Resolved slot for Annexure(s) row (matches upload order). Clamped so the row always renders. */
  getResolvedAnnexureInsertAfterIndex(): number {
    const len = this.structuredRows.length;
    if (len === 0) {
      return -1;
    }
    const last = len - 1;
    let raw: number;
    const passed = this.annexureUiInsertAfterRowIndex;
    if (typeof passed === "number" && !Number.isNaN(passed)) {
      raw = passed;
    } else {
      const v = this.getVakalatnamaIndex();
      if (v >= 0) raw = v - 1;
      else raw = last;
    }
    return Math.min(Math.max(raw, -1), last);
  }

  showAnnexureSlotBeforeAllRows(): boolean {
    return (
      this.enableAnnexureSequence && this.getResolvedAnnexureInsertAfterIndex() < 0
    );
  }

  showAnnexureSlotAfterRow(rowIdx: number): boolean {
    return (
      this.enableAnnexureSequence &&
      this.getResolvedAnnexureInsertAfterIndex() === rowIdx
    );
  }

  private getCurrentUploadItemCount(): number {
    if (this.isStructuredMode()) {
      return (
        this.structuredRows.filter((row) => !!row.file).length +
        this.annexureRows.filter((row) => !!row.file).length
      );
    }
    return this.entries.length;
  }

  getOverallUploadProgress(): number {
    const totalItems = this.getCurrentUploadItemCount();
    if (totalItems <= 0) return 0;

    let sum = 0;
    for (let index = 0; index < totalItems; index += 1) {
      sum += this.getFileProgress(index);
    }

    return Math.round(sum / totalItems);
  }

  hasUploadedAllStructuredDocuments(): boolean {
    if (!this.isStructuredMode()) return false;
    if (this.structuredRows.length === 0) return false;

    const uploaded = new Set(
      (this.existingIndexNames || [])
        .map((name) => String(name || "").trim().toLowerCase())
        .filter((name) => !!name),
    );

    const allMandatoryUploaded = this.structuredRows.every((row) =>
      uploaded.has(String(row.index_name || "").trim().toLowerCase()),
    );

    if (!allMandatoryUploaded) return false;
    if (!this.enableAnnexureSequence) return true;

    return Array.from(uploaded).some((name) =>
      /annexure\s+[arp]\s*\d+/i.test(String(name).replace(/\s+/g, " ").trim()),
    );
  }

  shouldShowStructuredUploadTable(): boolean {
    if (!this.structuredIndexUpload) return false;
    return !this.hasUploadedAllStructuredDocuments();
  }

  private syncStructuredFinalDocument() {
    const first =
      this.structuredRows.find((r) => !!r.file)?.file ||
      this.annexureRows.find((r) => !!r.file)?.file ||
      null;
    this.form?.patchValue({ final_document: first });
  }

  onFlatAnnexureFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;
    this.appendFlatAnnexureFiles(Array.from(input.files));
    input.value = "";
    this.cdr.markForCheck();
    this.cdr.detectChanges();
  }

  private appendFlatAnnexureFiles(files: File[]) {
    const { valid, errors } = validatePdfFiles(files);
    if (errors.length > 0) {
      this.toastr.error(errors.join(" "));
    }
    if (valid.length === 0) return;

    const letter = this.getAnnexureLetter();
    let n = this.maxFlatAnnexureSuffixForLetter(letter) + 1;
    const annexureEntries: DocumentUploadEntry[] = valid.map((file) => {
      const idx = `Annexure ${letter}${n++}`;
      const matchedMaster = this.indexMasters.find(
        (item) => item.name.toLowerCase() === idx.toLowerCase(),
      );
      return {
        file,
        index_name: idx,
        index_id: matchedMaster ? matchedMaster.id : null,
        is_annexure: true,
      };
    });

    this.entries = [...this.entries, ...annexureEntries];
    this.annexureCounter = n;
    this.form.patchValue({
      final_document: this.entries.length > 0 ? this.entries[0].file : null,
    });
  }

  updateDocumentType(index: number, value: string) {
    const entry = this.entries[index];
    if (!entry) return;
    if (entry.is_annexure) return;
    const typedValue = String(value || "").trim();
    entry.index_name = typedValue;

    const normalized = typedValue.trim().toLowerCase();
    const matchedMaster = this.indexMasters.find(
      (item) => item.name.toLowerCase() === normalized,
    );
    entry.index_id = matchedMaster ? matchedMaster.id : null;
  }

  private getDocTypeDocuments(): string[] {
    const docTypeRows = docTypes as DocTypeOption[];

    const caseId = Number(this.caseTypeId || 0);
    if (!caseId) return [];

    const match = docTypeRows.find(
      (item) => Number(item.case_type_id) === caseId,
    );
    if (!match || !Array.isArray(match.documents)) return [];

    return match.documents.filter(
      (doc: string) => typeof doc === "string" && doc.trim().length > 0,
    );
  }

  getAvailableIndexNames(index: number): string[] {
    const allDocs = this.getDocumentIndexUniverse();
    const currentValue = String(this.entries?.[index]?.index_name || "").trim();
    const currentNormalized = currentValue.toLowerCase();
    const selected = new Set(
      this.entries
        .map((entry, i) =>
          i === index
            ? ""
            : String(entry.index_name || "")
                .trim()
                .toLowerCase(),
        )
        .filter((value) => value.length > 0),
    );
    const alreadyUploaded = new Set(
      (this.existingIndexNames || [])
        .map((name) =>
          String(name || "")
            .trim()
            .toLowerCase(),
        )
        .filter((name) => name.length > 0),
    );

    return allDocs.filter((name) => {
      const normalized = String(name || "")
        .trim()
        .toLowerCase();
      return (
        (!selected.has(normalized) || normalized === currentNormalized) &&
        (!alreadyUploaded.has(normalized) || normalized === currentNormalized)
      );
    });
  }

  private getDocumentIndexUniverse(): string[] {
    const base = this.getDocTypeDocuments();
    if (this.mandatoryIndexNames?.length) {
      const L = this.getAnnexureLetter();
      const annexureItems = this.enableAnnexureSequence
        ? Array.from({ length: 15 }, (_, i) => `Annexure ${L}${i + 1}`)
        : [];
      return [...this.mandatoryIndexNames, ...annexureItems];
    }
    return base;
  }

  private getAutoIndexName(): string {
    if (!this.mandatoryIndexNames?.length) return "";

    const mandatoryNoAnnexure = this.mandatoryIndexNames

    if (this.mandatoryIndexCursor < mandatoryNoAnnexure.length) {
      return mandatoryNoAnnexure[this.mandatoryIndexCursor++];
    }

    if (this.enableAnnexureSequence) {
      const L = this.getAnnexureLetter();
      return `Annexure ${L}${this.annexureCounter++}`;
    }
    return "";
  }

  getIndexSuggestions(query: string): string[] {
    const q = (query || "").trim().toLowerCase();
    if (!q) return [];

    return this.indexMasters
      .map((item) => item.name)
      .filter((name) => name.toLowerCase().includes(q))
      .slice(0, 12);
  }

  trackByEntry(index: number, entry: DocumentUploadEntry): File {
    return entry.file;
  }

  trackByAnnexureEntry(index: number, entry: DocumentUploadEntry): string {
    const f = entry.file;
    return `${entry.index_name}:${f.name}:${f.size}:${f.lastModified}:${index}`;
  }

  removeEntry(index: number) {
    this.entries = this.entries.filter((_, i) => i !== index);

    this.form.patchValue({
      final_document: this.entries.length > 0 ? this.entries[0].file : null,
    });
  }

  /** Delete row by index in `getAnnexureEntries()` (not `entries` index). */
  removeAnnexureEntryAt(annexureViewIndex: number) {
    const annexures = this.getAnnexureEntries();
    const target = annexures[annexureViewIndex];
    if (!target) return;
    const global = this.entries.indexOf(target);
    if (global < 0) return;
    this.removeEntry(global);
    this.cdr.markForCheck();
    this.cdr.detectChanges();
  }

  reorderEntries(event: CdkDragDrop<DocumentUploadEntry[]>) {
    if (this.isUploading) return;
    moveItemInArray(this.entries, event.previousIndex, event.currentIndex);
  }

  isAnnexureEntry(entry: DocumentUploadEntry): boolean {
    return !!entry?.is_annexure;
  }

  getAnnexureEntries(): DocumentUploadEntry[] {
    return this.entries.filter((entry) => !!entry.is_annexure);
  }

  private resolveDefaultDocumentType(): string {
    const provided = String(this.defaultDocumentType || "").trim();
    if (provided) return provided;
    return "New Filing";
  }

  getEffectiveDocumentType(): string {
    const resolved = this.resolveDefaultDocumentType();
    if (resolved) return resolved;
    return String(this.form?.value?.document_type || "").trim();
  }

  canUpload(): boolean {
    if (this.isStructuredMode()) {
      const hasAllMandatory = this.structuredRows.every((row) => !!row.file);
      const hasAnnexure = !this.enableAnnexureSequence
        ? true
        : this.annexureRows.length > 0;
      const allAnnexuresFilled = this.annexureRows.every((row) => !!row.file);
      return !this.isUploading && hasAllMandatory && hasAnnexure && allAnnexuresFilled;
    }
    if (this.useTextIndexName) {
      const hasParentName =
        !this.useParentIndexGroup ||
        !!String(this.parentGroupName || "").trim();
      if (this.multiManualIndexRows) {
        if (!hasParentName || this.isUploading) return false;
        const rows = this.manualIndexRows;
        const partial = rows.some((r) => {
          const hasN = !!String(r.indexName || "").trim();
          const hasF = !!r.file;
          return hasN !== hasF;
        });
        if (partial) return false;
        const complete = rows.filter(
          (r) => r.file && String(r.indexName || "").trim(),
        );
        return complete.length >= 1;
      }
      return (
        !this.isUploading &&
        !!this.stagedFile &&
        !!String(this.stagedIndexName || "").trim() &&
        hasParentName
      );
    }
    return (
      !this.isUploading &&
      this.entries.length > 0 &&
      this.entries.every(
        (entry) => entry.index_name && entry.index_name.trim().length > 0,
      )
    );
  }

  onMemoAppealFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] || null;
    if (!file) return;
    const { valid, errors } = validatePdfFiles([file]);
    if (errors.length > 0) {
      this.toastr.error(errors.join(" "));
      input.value = "";
      return;
    }
    this.memoAppealFile = valid[0] || null;
    input.value = "";
  }

  clearMemoAppealFile() {
    this.memoAppealFile = null;
  }

  clearMemoAppealWithInput(input: HTMLInputElement | null) {
    this.memoAppealFile = null;
    if (input) input.value = "";
  }

  submitMemoAppeal() {
    if (
      !this.enableMemoOfAppeal ||
      this.memoAlreadyUploaded ||
      this.isUploading
    ) {
      return;
    }
    if (!this.memoAppealFile) {
      this.toastr.warning("Select a PDF for the memo of appeal.");
      return;
    }
    const idxName = MEMO_OF_APPEAL_INDEX_NAME;
    const matched = this.indexMasters.find(
      (item) => item.name.toLowerCase() === idxName.toLowerCase(),
    );
    this.submitDoc.emit({
      document_type: MEMO_OF_APPEAL_DOCUMENT_TYPE,
      items: [
        {
          file: this.memoAppealFile,
          index_name: idxName,
          index_id: matched ? matched.id : null,
        },
      ],
    });
  }

  submit() {
    if (this.isSubmitting) return;
    this.submitAttempted = true;
    if (!this.canUpload()) return;
    this.isSubmitting = true;

    const items = this.isStructuredMode()
      ? this.getStructuredItemsInRequiredOrder()
      : this.useTextIndexName
        ? this.getTextModeItems()
        : this.entries.map((entry) => ({
            file: entry.file,
            index_name: entry.index_name.trim(),
            index_id: entry.index_id,
          }));

    const payload: UploadDocumentsPayload = {
      document_type: this.getEffectiveDocumentType(),
      items,
    };
    if (this.useTextIndexName && this.useParentIndexGroup) {
      const g = String(this.parentGroupName || "").trim();
      if (g) payload.parent_group_name = g;
    }
    // console.log(payload);
    this.submitDoc.emit(payload);
    this.submitAttempted = false;
  }

  private getTextModeItems(): UploadDocumentsPayloadItem[] {
    if (this.multiManualIndexRows) {
      const manualItems = this.manualIndexRows
        .filter((r) => r.file && String(r.indexName || "").trim())
        .map((r) => {
          const name = String(r.indexName).trim();
          const matched = this.indexMasters.find(
            (item) => item.name.toLowerCase() === name.toLowerCase(),
          );
          return {
            file: r.file as File,
            index_name: name,
            index_id: matched ? matched.id : null,
          };
        });
      const annexures = this.getAnnexureEntries().map((entry) => ({
        file: entry.file,
        index_name: entry.index_name.trim(),
        index_id: entry.index_id,
      }));
      return [...manualItems, ...annexures];
    }
    const mainIndexName = String(this.stagedIndexName || "").trim();
    const mainFile = this.stagedFile;
    const mainMatched = this.indexMasters.find(
      (item) => item.name.toLowerCase() === mainIndexName.toLowerCase(),
    );
    const mainItem: UploadDocumentsPayloadItem | null =
      mainFile && mainIndexName
        ? {
            file: mainFile,
            index_name: mainIndexName,
            index_id: mainMatched ? mainMatched.id : null,
          }
        : null;
    const annexures = this.getAnnexureEntries().map((entry) => ({
      file: entry.file,
      index_name: entry.index_name.trim(),
      index_id: entry.index_id,
    }));
    return mainItem ? [mainItem, ...annexures] : annexures;
  }

  private getStructuredItemsInRequiredOrder(): UploadDocumentsPayloadItem[] {
    const k = this.getResolvedAnnexureInsertAfterIndex();
    let before: StructuredIndexRow[];
    let after: StructuredIndexRow[];
    if (k < 0) {
      before = [];
      after = [...this.structuredRows];
    } else {
      before = this.structuredRows.slice(0, k + 1);
      after = this.structuredRows.slice(k + 1);
    }
    const orderedRows = [...before, ...this.annexureRows, ...after];

    return orderedRows
      .filter((row) => !!row.file)
      .map((row) => ({
        file: row.file as File,
        index_name: row.index_name.trim(),
        index_id: row.index_id,
      }));
  }

  isIndexNameInvalid(entry: DocumentUploadEntry): boolean {
    if (!this.submitAttempted) return false;
    return !entry.index_name || entry.index_name.trim().length === 0;
  }

  getFileProgress(index: number): number {
    const progress = this.fileProgresses?.[index];
    if (typeof progress !== "number") return 0;
    return Math.min(100, Math.max(0, Math.round(progress)));
  }

  hasAnyProgress(): boolean {
    return (this.fileProgresses || []).some(
      (p) => typeof p === "number" && p > 0,
    );
  }

  canDownloadMerged(): boolean {
    return (
      !this.isUploading &&
      !this.isMerging &&
      this.entries.length > 0 &&
      this.entries.every((e) => e.index_name && e.index_name.trim().length > 0)
    );
  }

  downloadMergedPdf(): void {
    if (!this.canDownloadMerged()) return;
    const files = this.entries.map((e) => e.file);
    const names = this.entries.map((e) => e.index_name.trim());
    const frontPage = this.frontPage
      ? {
          petitionerName: this.frontPage.petitionerName || "",
          respondentName: this.frontPage.respondentName || "",
          caseNo: this.frontPage.caseNo || "",
          caseType: this.frontPage.caseType || "",
        }
      : undefined;
    this.isMerging = true;
    this.mergeError = null;
    this.eFilingService.mergePdfs(files, names, frontPage).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const docType =
          (this.getEffectiveDocumentType() || "Documents").replace(
            /[^a-zA-Z0-9_-]/g,
            "_",
          ) || "Documents";
        const efilingNo =
          (this.eFilingNumber || "").replace(/[^a-zA-Z0-9_-]/g, "") || "merged";
        a.download = `${docType}_${efilingNo}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
        this.isMerging = false;
      },
      error: (err) => {
        this.isMerging = false;
        const msg =
          (typeof err?.error === "object" &&
          err?.error !== null &&
          typeof err.error.error === "string"
            ? err.error.error
            : null) ||
          err?.message ||
          "Failed to merge PDFs.";
        this.mergeError = msg;
      },
    });
  }
}
