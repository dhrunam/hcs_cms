import { CommonModule } from "@angular/common";
import {
  Component,
  EventEmitter,
  Input,
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
  /** Index names already uploaded for this filing (avoid duplicates). */
  @Input() existingIndexNames: string[] = [];
  /** Enforce and auto-sequence mandatory indexes (e.g. WP(C) Main Petition). */
  @Input() mandatoryIndexNames: string[] = [];
  /** Enables Annexure A1/A2/... support and UI helper button. */
  @Input() enableAnnexureSequence = false;
  /** Render fixed index rows with per-row upload controls. */
  @Input() structuredIndexUpload = false;
  /** Use free-text input for index name instead of dropdown. */
  @Input() useTextIndexName = false;
  /**
   * With useTextIndexName: require a top-level "Name" for the parent index row (no file),
   * then upload indexes/annexures as children linked in the database.
   */
  @Input() useParentIndexGroup = false;
  /** Optional memo-of-appeal upload (separate document type); does not affect mandatory indexes. */
  @Input() enableMemoOfAppeal = false;
  /** When true, main filing already has a "Memo of Appeal" document — hide duplicate upload. */
  @Input() memoAlreadyUploaded = false;
  stagedIndexName = "";
  stagedFile: File | null = null;
  /** Parent EfilingDocumentsIndex.document_part_name (header row, no file) when useParentIndexGroup. */
  parentGroupName = "";
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
  ) {}

  ngOnInit(): void {
    const initialDocType = this.getEffectiveDocumentType();
    if (initialDocType) {
      this.form?.patchValue({ document_type: initialDocType });
    }
    this.eFilingService.get_document_index_master().subscribe({
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
              Number.isFinite(item.id) && !!item.name,
          );
      },
      error: () => {
        this.indexMasters = [];
      },
    });
    this.initializeStructuredRows();
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
      this.memoAppealFile = null;
      this.parentGroupName = "";
      this.initializeStructuredRows();
    }
    if (changes["mandatoryIndexNames"] || changes["structuredIndexUpload"]) {
      this.initializeStructuredRows();
    }
  }

  private isStructuredMode(): boolean {
    return this.structuredIndexUpload && this.mandatoryIndexNames.length > 0;
  }

  private initializeStructuredRows() {
    if (!this.isStructuredMode()) return;
    const baseRows = this.mandatoryIndexNames
      .filter((name) => name.trim().toLowerCase() !== "annexure(s)*")
      .map((name) => {
        const clean = String(name).trim();
        const matchedMaster = this.indexMasters.find(
          (item) => item.name.toLowerCase() === clean.toLowerCase(),
        );
        return {
          index_name: clean,
          index_id: matchedMaster ? matchedMaster.id : null,
          file: null,
        } as StructuredIndexRow;
      });
    this.structuredRows = baseRows;
    this.annexureRows = [];
    this.form?.patchValue({ final_document: null });
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
  }

  clearStagedFile() {
    this.stagedFile = null;
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
    const row = this.structuredRows[rowIndex];
    if (!row) return;
    row.file = valid[0];
    this.syncStructuredFinalDocument();
    input.value = "";
  }

  onAnnexureFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;
    const files = Array.from(input.files);
    const { valid, errors } = validatePdfFiles(files);
    if (errors.length > 0) {
      this.toastr.error(errors.join(" "));
    }
    valid.forEach((file) => {
      const name = `Annexure A${this.annexureCounter++}`;
      this.annexureRows.push({
        index_name: name,
        index_id: null,
        file,
      });
    });
    this.syncStructuredFinalDocument();
    input.value = "";
  }

  removeAnnexureRow(index: number) {
    this.annexureRows = this.annexureRows.filter((_, i) => i !== index);
    this.syncStructuredFinalDocument();
  }

  clearStructuredRowFile(index: number) {
    const row = this.structuredRows[index];
    if (!row) return;
    row.file = null;
    this.syncStructuredFinalDocument();
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

  getRowsBeforeAnnexure(): StructuredIndexRow[] {
    const vakalatnamaIndex = this.getVakalatnamaIndex();
    if (vakalatnamaIndex < 0) return this.structuredRows;
    return this.structuredRows.slice(0, vakalatnamaIndex);
  }

  getRowsAfterAnnexure(): StructuredIndexRow[] {
    const vakalatnamaIndex = this.getVakalatnamaIndex();
    if (vakalatnamaIndex < 0) return [];
    return this.structuredRows.slice(vakalatnamaIndex);
  }

  getStructuredRowIndex(row: StructuredIndexRow): number {
    return this.structuredRows.indexOf(row);
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

    // Annexure requirement is satisfied when any Annexure A* exists.
    return Array.from(uploaded).some((name) => name.startsWith("annexure a"));
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

  addAnnexure() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/pdf";
    input.multiple = true;
    input.onchange = (ev: Event) => {
      const target = ev.target as HTMLInputElement;
      if (!target.files?.length) return;
      const files = Array.from(target.files);
      const { valid, errors } = validatePdfFiles(files);
      if (errors.length > 0) {
        this.toastr.error(errors.join(" "));
      }
      if (valid.length === 0) return;

      const annexureEntries: DocumentUploadEntry[] = valid.map((file) => {
        const idx = `Annexure A${this.annexureCounter++}`;
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
      this.form.patchValue({
        final_document: this.entries.length > 0 ? this.entries[0].file : null,
      });
    };
    input.click();
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
      const annexureItems = this.enableAnnexureSequence
        ? Array.from({ length: 15 }, (_, i) => `Annexure A${i + 1}`)
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
      return `Annexure A${this.annexureCounter++}`;
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

  removeEntry(index: number) {
    this.entries = this.entries.filter((_, i) => i !== index);

    this.form.patchValue({
      final_document: this.entries.length > 0 ? this.entries[0].file : null,
    });
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
      return !this.isUploading && hasAllMandatory && hasAnnexure;
    }
    if (this.useTextIndexName) {
      const hasParentName =
        !this.useParentIndexGroup ||
        !!String(this.parentGroupName || "").trim();
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
    const orderedRows = [
      ...this.getRowsBeforeAnnexure(),
      ...this.annexureRows,
      ...this.getRowsAfterAnnexure(),
    ];

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
