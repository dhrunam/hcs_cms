import { CommonModule } from "@angular/common";
import { HttpEventType } from "@angular/common/http";
import { Component, OnInit } from "@angular/core";
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import { RouterLink } from "@angular/router";
import { firstValueFrom } from "rxjs";
import { forkJoin } from "rxjs";
import { ToastrService } from "ngx-toastr";
import Swal from "sweetalert2";

import { app_url } from "../../../../../../environment";
import { EfilingService } from "../../../../../../services/advocate/efiling/efiling.services";
import {
  getValidationErrorMessage,
  validatePdfFiles,
  validatePdfOcrForFiles,
} from "../../../../../../utils/pdf-validation";
import {
  formatPartyLine,
  formatPetitionerVsRespondent,
  getOrderedPartyNames,
} from "../../../../../../utils/petitioner-vs-respondent";
import { UploadDocuments } from "../../new-filing/upload-documents/upload-documents";

@Component({
  selector: "app-document-filing-create",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
    UploadDocuments,
  ],
  templateUrl: "./create.html",
  styleUrl: "./create.css",
})
export class Create implements OnInit {
  uploadFilingDocForm!: FormGroup;
  filings: any[] = [];
  filingsWithLitigants: Array<{ filing: any; litigants: any[] }> = [];
  searchQuery = "";
  isDropdownOpen = false;
  selectedFiling: any = null;

  iaList: any[] = [];
  iaSearchQuery = "";
  iaDropdownOpen = false;
  selectedIa: any = null;

  isLoadingFilings = true;
  isLoadingCase = false;
  caseDetails: any = null;

  existingDocList: any[] = [];
  uploadedDocList: any[] = [];

  isUploadingDocuments = false;
  private isUploadRequestInFlight = false;
  isMergingPdf = false;
  mergeError: string | null = null;
  uploadFileProgresses: number[] = [];
  uploadCompletedToken = 0;

  selectedEfilingId: number | null = null;
  selectedEfilingNumber = "";
  documentTypeOptions: any[] = [];
  isDocumentTypeDropdownOpen = false;
  documentTypeSearchQuery = "";
  selectedDocumentType = "";

  constructor(
    private fb: FormBuilder,
    private eFilingService: EfilingService,
    private toastr: ToastrService,
  ) {
    this.uploadFilingDocForm = this.fb.group({
      document_type: ["", Validators.required],
      final_document: [null],
    });
  }

  ngOnInit(): void {
    this.loadFilings();
  }

  loadFilings(): void {
    this.isLoadingFilings = true;
    this.eFilingService.get_filings().subscribe({
      next: (data: any) => {
        this.filings = data.results.filter(
          (f: any) => f?.id && f?.e_filing_number,
        );
        this.loadLitigantsForFilings();
        console.log("Filings are", this.filings);
      },
      error: () => {
        this.filings = [];
        this.isLoadingFilings = false;
      },
    });
  }

  get_document_index_for_existing_filing(id: number) {
    this.eFilingService.get_document_index_for_existing_filing(id).subscribe({
      next: (data) => {
        this.documentTypeOptions = data.results.sort(
          (a: any, b: any) => a.sequence_number - b.sequence_number,
        );
        console.log(
          "After calling get document index by case type api",
          this.documentTypeOptions,
        );
      },
    });
  }

  private loadLitigantsForFilings(): void {
    if (this.filings.length === 0) {
      this.filingsWithLitigants = [];
      this.isLoadingFilings = false;
      return;
    }
    const requests = this.filings.map((f) =>
      this.eFilingService.get_litigant_list_by_filing_id(Number(f.id)),
    );
    forkJoin(requests).subscribe({
      next: (litigantResults) => {
        this.filingsWithLitigants = this.filings.map((filing, i) => {
          const list = Array.isArray(litigantResults[i])
            ? litigantResults[i]
            : (litigantResults[i]?.results ?? []);
          return { filing, litigants: list };
        });
        this.isLoadingFilings = false;
      },
      error: () => {
        this.filingsWithLitigants = this.filings.map((f) => ({
          filing: f,
          litigants: [],
        }));
        this.isLoadingFilings = false;
      },
    });
  }

  get filteredFilingsWithLitigants(): Array<{ filing: any; litigants: any[] }> {
    const q = (this.searchQuery || "").trim().toLowerCase();
    if (!q) return this.filingsWithLitigants;
    return this.filingsWithLitigants.filter((item) => {
      const ef = (item.filing.e_filing_number || "").toLowerCase();
      const ct = (item.filing.case_type?.type_name || "").toLowerCase();
      const pn = (item.filing.petitioner_name || "").toLowerCase();
      const petNames = getOrderedPartyNames(item.litigants, true)
        .join(" ")
        .toLowerCase();
      const resNames = getOrderedPartyNames(item.litigants, false)
        .join(" ")
        .toLowerCase();
      const vsLine = this.getLitigantLabel(item).toLowerCase();
      return (
        ef.includes(q) ||
        ct.includes(q) ||
        pn.includes(q) ||
        petNames.includes(q) ||
        resNames.includes(q) ||
        vsLine.includes(q)
      );
    });
  }

  getLitigantLabel(item: { filing: any; litigants: any[] }): string {
    return (
      formatPetitionerVsRespondent(
        item.litigants,
        String(item.filing?.petitioner_name || ""),
      ) || "—"
    );
  }

  selectFiling(item: { filing: any }): void {
    console.log("Selected item for filing is", item);
    console.log(item.filing.case_type.id);

    this.get_document_index_for_existing_filing(item.filing.case_type.id);
    this.selectedFiling = item.filing;
    this.selectedEfilingId = item.filing.id;
    this.selectedEfilingNumber = String(item.filing.e_filing_number ?? "");
    this.isDropdownOpen = false;
    this.searchQuery = "";
    this.selectedIa = null;
    this.uploadedDocList = [];
    this.selectedDocumentType = "";
    this.documentTypeSearchQuery = "";
    this.uploadFilingDocForm.reset();
    this.loadIasForFiling();
    this.loadSelectedCaseDetailsAndDocs();
  }

  private loadIasForFiling(): void {
    if (!this.selectedEfilingId) {
      this.iaList = [];
      return;
    }
    this.eFilingService
      .get_ias_by_efiling_id(this.selectedEfilingId)
      .subscribe({
        next: (res) => {
          const rows = Array.isArray(res) ? res : (res?.results ?? []);
          this.iaList = rows.filter((ia: any) => ia?.id);
        },
        error: () => {
          this.iaList = [];
        },
      });
  }

  get filteredIaList(): any[] {
    const q = (this.iaSearchQuery || "").trim().toLowerCase();
    if (!q) return this.iaList;
    return this.iaList.filter((ia) => {
      const iaNum = (ia?.ia_number ?? "").toLowerCase();
      const iaText = (ia?.ia_text ?? "").toLowerCase();
      const status = (ia?.status ?? "").toLowerCase();
      return iaNum.includes(q) || iaText.includes(q) || status.includes(q);
    });
  }

  selectIa(ia: any): void {
    this.selectedIa = ia;
    this.iaDropdownOpen = false;
    this.iaSearchQuery = "";
  }

  getSelectedIaLabel(): string {
    if (!this.selectedIa) return "";
    const iaNum = this.selectedIa.ia_number || "-";
    const status = this.selectedIa.status || "Pending";
    const snippet = (this.selectedIa.ia_text || "").slice(0, 50);
    return `${iaNum} (${status})${snippet ? " - " + snippet + (this.selectedIa.ia_text?.length > 50 ? "..." : "") : ""}`;
  }

  trackIa(_: number, ia: any): number {
    return ia?.id ?? 0;
  }

  getIaStatusBadgeClass(status: string | null): string {
    const s = (status ?? "").trim().toLowerCase();
    if (s.includes("accept")) return "status-badge-success";
    if (s.includes("reject") || s.includes("partial"))
      return "status-badge-danger";
    return "status-badge-warning";
  }

  getSelectedLabel(): string {
    if (!this.selectedFiling) return "";
    const item = this.filingsWithLitigants.find(
      (x) => x.filing.id === this.selectedFiling.id,
    );
    if (!item)
      return `${this.selectedFiling.e_filing_number} | ${this.selectedFiling.case_type?.type_name || "N/A"}`;
    return `${this.selectedFiling.e_filing_number} | ${this.selectedFiling.case_type?.type_name || "N/A"} | ${this.getLitigantLabel(item)}`;
  }

  private loadSelectedCaseDetailsAndDocs(): void {
    if (!this.selectedEfilingId) return;

    this.isLoadingCase = true;
    this.caseDetails = null;
    this.existingDocList = [];

    forkJoin({
      caseDetails: this.eFilingService.get_case_details_by_filing_id(
        this.selectedEfilingId,
      ),
      documents: this.eFilingService.get_documents_by_filing_id(
        this.selectedEfilingId,
      ),
      documentIndexes: this.eFilingService.get_document_reviews_by_filing_id(
        this.selectedEfilingId,
        false,
      ),
    }).subscribe({
      next: ({ caseDetails, documents, documentIndexes }) => {
        const caseRows = caseDetails?.results ?? [];
        this.caseDetails = caseRows?.[0] ?? null;

        const mainDocs = documents?.results ?? [];
        const indexParts = documentIndexes?.results ?? [];

        this.existingDocList = mainDocs.map((doc: any) => {
          const partsForDoc = indexParts
            .filter((p: any) => Number(p.document) === Number(doc.id))
            .sort(
              (a: any, b: any) =>
                Number(a.document_sequence) - Number(b.document_sequence),
            );

          return {
            ...doc,
            document_indexes: partsForDoc,
          };
        });

        this.isLoadingCase = false;
      },
      error: () => {
        this.isLoadingCase = false;
        this.toastr.error("Failed to load case details.");
      },
    });
  }

  deleteDoc(id: number, index: number): void {
    const confirmDelete = confirm(
      "Your document will be deleted and you need to re-upload it. Continue?",
    );
    if (!confirmDelete) return;

    this.eFilingService
      .delete_case_documnets_before_final_filing(id)
      .subscribe({
        next: () => {
          this.uploadedDocList.splice(index, 1);
          this.toastr.success("Document deleted.");
        },
        error: () => {
          this.toastr.error("Failed to delete document.");
        },
      });
  }

  trackByDocId(_: number, item: any): number {
    return item?.id ?? 0;
  }

  private maxDocumentSequence(parts: any[]): number {
    if (!Array.isArray(parts) || parts.length === 0) return 0;
    return parts.reduce(
      (m, p) => Math.max(m, Number(p?.document_sequence) || 0),
      0,
    );
  }

  getDocDisplayLabel(doc: any): string {
    if (doc?.ia_number && doc?.document_type === "IA") return doc.ia_number;
    return doc?.document_type || "-";
  }

  isWpcCaseTypeSelected(): boolean {
    const raw = String(
      this.selectedFiling?.case_type?.type_name ||
        this.selectedFiling?.case_type?.full_form ||
        "",
    )
      .trim()
      .toUpperCase();
    const normalized = raw.replace(/\s+/g, "");
    return normalized === "WP(C)";
  }

  trackFilingItem(_: number, item: { filing: any }): number {
    return item?.filing?.id ?? 0;
  }

  // get filteredDocumentTypeOptions(): string[] {
  //   const q = String(this.documentTypeSearchQuery || "")
  //     .trim()
  //     .toLowerCase();
  //   if (!q) return this.documentTypeOptions;
  //   return this.documentTypeOptions.filter((x) => x.toLowerCase().includes(q));
  // }

  selectDocumentType(option: any): void {
    this.selectedDocumentType = option;
    this.documentTypeSearchQuery = "";
    this.isDocumentTypeDropdownOpen = false;
  }

  getSelectedDocumentTypeLabel(): string {
    return this.selectedDocumentType || "";
  }

  private isDocumentVerified(doc: any): boolean {
    const indexes = doc?.document_indexes ?? [];
    if (indexes.length === 0) return false;
    return indexes.every((p: any) => {
      const s = (p?.scrutiny_status ?? "").trim().toLowerCase();
      return s.includes("accept");
    });
  }

  get verifiedDocList(): any[] {
    return this.existingDocList.filter((doc) => this.isDocumentVerified(doc));
  }

  get nonVerifiedDocList(): any[] {
    return this.existingDocList.filter((doc) => !this.isDocumentVerified(doc));
  }

  async handleDocUpload(data: any): Promise<void> {
    if (this.isUploadingDocuments || this.isUploadRequestInFlight) return;
    this.isUploadRequestInFlight = true;
    try {
      const documentType = String(data?.document_type || "").trim();
      const uploadItems = Array.isArray(data?.items) ? data.items : [];

      if (
        !documentType ||
        uploadItems.length === 0 ||
        !this.selectedEfilingId
      ) {
        this.toastr.warning(
          "Please select an E-Filing and add documents with document type and index names.",
        );
        return;
      }

      // Validate PDF size (≤ 25 MB) and OCR before confirmation
      const files = uploadItems.map((i: any) => i.file).filter(Boolean);
      const { valid, errors } = validatePdfFiles(files);
      if (errors.length > 0) {
        this.toastr.error(errors.join(" "));
        return;
      }
      if (valid.length !== files.length) {
        this.toastr.error(
          "Some files could not be validated. Please ensure all files are PDFs under 25 MB.",
        );
        return;
      }

      const ocrError = await validatePdfOcrForFiles(valid);
      if (ocrError) {
        this.toastr.error(ocrError);
        return;
      }

      const targetLabel = this.selectedIa
        ? `the selected IA (${this.selectedIa.ia_number || ""})`
        : "the selected e-filing";
      const proceed = await this.promptOtpAndProceed(
        "File Documents?",
        `Upload these documents to ${targetLabel}.`,
      );
      if (!proceed) return;

      this.isUploadingDocuments = true;
      this.uploadFileProgresses = uploadItems.map(() => 0);

      const documentPayload = new FormData();
      documentPayload.append("document_type", documentType);
      documentPayload.append("e_filing", String(this.selectedEfilingId));
      documentPayload.append("e_filing_number", this.selectedEfilingNumber);

      if (this.selectedIa) {
        documentPayload.append("is_ia", "true");
        documentPayload.append(
          "ia_number",
          String(this.selectedIa.ia_number ?? ""),
        );
      } else {
        documentPayload.append("is_ia", "false");
      }

      const documentRes = await firstValueFrom(
        this.eFilingService.upload_case_documnets(documentPayload),
      );
      const documentId = documentRes?.id;
      if (!documentId) throw new Error("Document creation failed");

      const existingIndexes = Array.isArray(documentRes?.document_indexes)
        ? documentRes.document_indexes
        : [];
      let nextSeq = this.maxDocumentSequence(existingIndexes);
      const uploadedDocumentParts: any[] = [];
      const groupName = String(data?.parent_group_name ?? "").trim();
      let parentIndexId: number | null = null;

      if (groupName) {
        nextSeq += 1;
        const parentFd = new FormData();
        parentFd.append("document", String(documentId));
        parentFd.append("document_part_name", groupName);
        parentFd.append("document_sequence", String(nextSeq));
        const parentRes = await firstValueFrom(
          this.eFilingService.createDocumentIndexMetadata(parentFd),
        );
        parentIndexId = parentRes?.id != null ? Number(parentRes.id) : null;
        if (parentRes) uploadedDocumentParts.push(parentRes);
      }

      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];
        nextSeq += 1;
        const indexPayload = new FormData();
        indexPayload.append("document", String(documentId));
        indexPayload.append(
          "document_part_name",
          String(item.index_name || "").trim(),
        );
        indexPayload.append("file_part_path", item.file);
        indexPayload.append("document_sequence", String(nextSeq));
        if (item.index_id) {
          indexPayload.append("index", String(item.index_id));
        }
        if (parentIndexId != null) {
          indexPayload.append("parent_document_index", String(parentIndexId));
        }

        const indexRes = await this.uploadIndexFileWithProgress(
          indexPayload,
          i,
        );
        uploadedDocumentParts.push(indexRes);
      }

      const firstFileUrl = uploadedDocumentParts.find(
        (p: any) => p?.file_url || p?.file_part_path,
      );
      this.uploadedDocList.push({
        ...documentRes,
        document_indexes: uploadedDocumentParts,
        final_document:
          firstFileUrl?.file_url ||
          firstFileUrl?.file_part_path ||
          documentRes?.final_document,
      });

      this.uploadCompletedToken++;
      this.toastr.success("Documents uploaded successfully.");
    } catch (error) {
      console.error("Document upload failed", error);
      const msg = getValidationErrorMessage(error);
      const friendlyMsg =
        !msg || /bad request|http error|400/i.test(msg)
          ? "Failed to upload documents. Please ensure all PDFs are under 25 MB and OCR-converted (searchable)."
          : msg;
      this.toastr.error(friendlyMsg);
    } finally {
      this.isUploadingDocuments = false;
      this.isUploadRequestInFlight = false;
    }
  }

  private async promptOtpAndProceed(
    title: string,
    text: string,
  ): Promise<boolean> {
    const confirmed = await Swal.fire({
      title,
      text,
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, Proceed",
      cancelButtonText: "Cancel",
    });
    if (!confirmed.isConfirmed) return false;

    this.toastr.success("OTP has been sent successfully.", "", {
      timeOut: 3000,
      closeButton: true,
    });

    let resolved = false;
    return new Promise<boolean>((resolve) => {
      const finish = (value: boolean) => {
        if (resolved) return;
        resolved = true;
        resolve(value);
      };

      Swal.fire({
        title: "Enter OTP",
        html:
          '<div style="display:flex;gap:8px;justify-content:center">' +
          ["otp-1", "otp-2", "otp-3", "otp-4"]
            .map(
              (id) =>
                `<input id="${id}" type="text" inputmode="numeric" maxlength="1" style="width:48px;height:48px;text-align:center;font-size:20px;border:1px solid #d1d5db;border-radius:8px;" />`,
            )
            .join("") +
          '<div id="otp-status" style="margin-top:12px;font-size:14px;text-align:center"></div>',
        showCancelButton: true,
        showConfirmButton: false,
        allowOutsideClick: false,
        didOpen: () => {
          const ids = ["otp-1", "otp-2", "otp-3", "otp-4"];
          const inputs = ids
            .map((id) => document.getElementById(id) as HTMLInputElement | null)
            .filter((el): el is HTMLInputElement => !!el);
          const statusEl = document.getElementById("otp-status");

          const setStatus = (message: string, color: string) => {
            if (!statusEl) return;
            statusEl.textContent = message;
            statusEl.style.color = color;
          };

          const getOtp = () => inputs.map((el) => el.value || "").join("");

          const validateOtp = () => {
            const otp = getOtp();
            if (otp.length < 4) {
              setStatus("", "");
              return;
            }
            if (otp !== "0000") {
              setStatus("OTP error. Please try again.", "#dc2626");
              return;
            }
            setStatus("OTP verified.", "#16a34a");
            Swal.close();
            finish(true);
          };

          inputs.forEach((input, index) => {
            input.addEventListener("input", () => {
              input.value = input.value.replace(/\D/g, "").slice(0, 1);
              if (input.value && inputs[index + 1]) inputs[index + 1].focus();
              validateOtp();
            });
            input.addEventListener("keydown", (event) => {
              if (
                event.key === "Backspace" &&
                !input.value &&
                inputs[index - 1]
              ) {
                inputs[index - 1].focus();
              }
            });
          });
          inputs[0]?.focus();
        },
      }).then((result) => {
        if (result.dismiss === Swal.DismissReason.cancel) finish(false);
      });
    });
  }

  /** Merge items from uploaded documents only (not existing docs). */
  private getMergeItems(): { url: string; name: string }[] {
    const items: { url: string; name: string }[] = [];
    const list = [...this.uploadedDocList];
    for (const doc of list) {
      const indexes = doc?.document_indexes;
      if (Array.isArray(indexes) && indexes.length > 0) {
        for (const part of indexes) {
          const url = part?.file_url || part?.file_part_path;
          if (url) {
            const name =
              part?.document_part_name?.trim() ||
              doc?.document_type ||
              "Document";
            items.push({ url, name });
          }
        }
      } else if (doc?.final_document) {
        const url = doc.final_document;
        const name = doc?.document_type?.trim() || "Document";
        items.push({ url, name });
      }
    }
    return items;
  }

  private toAbsoluteUrl(url: string): string {
    if (!url) return "";
    const s = String(url).trim();
    if (s.startsWith("http://") || s.startsWith("https://")) return s;
    const base = app_url.replace(/\/$/, "");
    return s.startsWith("/") ? `${base}${s}` : `${base}/${s}`;
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
      this.eFilingService.fetch_document_blob(this.toAbsoluteUrl(item.url)),
    );

    forkJoin(fetches).subscribe({
      next: (blobs) => {
        const files = blobs.map((blob, i) => {
          const name = items[i].name.replace(/\.pdf$/i, "") + ".pdf";
          return new File([blob], name, { type: "application/pdf" });
        });
        const names = items.map((i) => i.name);
        const row = this.filingsWithLitigants.find(
          (f) => f.filing.id === this.selectedEfilingId,
        );
        const litigants = row?.litigants ?? [];
        const pnFallback = String(
          this.selectedFiling?.petitioner_name || "",
        ).trim();
        const frontPage = {
          petitionerName: formatPartyLine(
            getOrderedPartyNames(litigants, true),
            pnFallback,
          ),
          respondentName: formatPartyLine(
            getOrderedPartyNames(litigants, false),
            "",
          ),
          caseNo: (this.selectedFiling?.e_filing_number || "").trim(),
          caseType:
            this.selectedFiling?.case_type?.full_form ||
            this.selectedFiling?.case_type?.type_name ||
            "",
        };

        this.eFilingService.mergePdfs(files, names, frontPage).subscribe({
          next: (mergedBlob) => {
            const url = URL.createObjectURL(mergedBlob);
            const a = document.createElement("a");
            a.href = url;
            const docType =
              (this.uploadedDocList[0]?.document_type || "Documents")
                .trim()
                .replace(/[^a-zA-Z0-9_-]/g, "_")
                .replace(/_+/g, "_")
                .replace(/^_|_$/g, "") || "Documents";
            const efilingNo =
              (this.selectedEfilingNumber || "").replace(
                /[^a-zA-Z0-9_-]/g,
                "",
              ) || "merged";
            a.download = `${docType}_${efilingNo}.pdf`;
            a.click();
            URL.revokeObjectURL(url);
            this.isMergingPdf = false;
          },
          error: (err) => {
            this.isMergingPdf = false;
            this.mergeError =
              err?.error?.error || err?.message || "Failed to merge PDFs.";
          },
        });
      },
      error: () => {
        this.isMergingPdf = false;
        this.mergeError = "Failed to fetch documents.";
      },
    });
  }

  private uploadIndexFileWithProgress(
    formData: FormData,
    index: number,
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      this.eFilingService.upload_case_documnets_index(formData).subscribe({
        next: (event: any) => {
          if (event.type === HttpEventType.UploadProgress) {
            const total = event.total || 0;
            if (total > 0) {
              this.uploadFileProgresses[index] = Math.round(
                (event.loaded / total) * 100,
              );
            }
          }

          if (event.type === HttpEventType.Response) {
            this.uploadFileProgresses[index] = 100;
            resolve(event.body);
          }
        },
        error: (err) => reject(err),
      });
    });
  }
}
