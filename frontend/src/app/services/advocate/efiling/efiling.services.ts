import { HttpClient, HttpEvent, HttpParams } from "@angular/common/http";
import { Observable, catchError, throwError } from "rxjs";
import { Injectable } from "@angular/core";
import { app_url } from "../../../environment";

export interface DistinctBenchOption {
  bench_code: string;
  bench_name: string | null;
}

@Injectable({ providedIn: "root" })
export class EfilingService {
  constructor(private http: HttpClient) {}

  post_efiling_initial_details(fd: FormData): Observable<any> {
    return this.http.post<any>(`${app_url}/api/v1/efiling/efilings/`, fd);
  }

  post_litigant_details(fd: FormData): Observable<any> {
    return this.http.post<any>(
      `${app_url}/api/v1/efiling/efiling-litigants/`,
      fd,
    );
  }
  update_litigant_details(fd: FormData): Observable<any> {
    var id = fd.get("id");
    return this.http.put<any>(
      `${app_url}/api/v1/efiling/efiling-litigants/${id}/`,
      fd,
    );
  }

  delete_litigant_details_by_id(id: number): Observable<any> {
    return this.http.delete<any>(
      `${app_url}/api/v1/efiling/efiling-litigants/${id}/`,
    );
  }

  post_case_details(fd: FormData): Observable<any> {
    return this.http.post<any>(
      `${app_url}/api/v1/efiling/efiling-case-details/`,
      fd,
    );
  }

  upload_case_documnets(fd: FormData): Observable<any> {
    return this.http.post<any>(
      `${app_url}/api/v1/efiling/efiling-documents/`,
      fd,
    );
  }

  upload_case_documnets_index(fd: FormData): Observable<HttpEvent<any>> {
    return this.http.post<any>(
      `${app_url}/api/v1/efiling/efiling-documents-index/`,
      fd,
      {
        reportProgress: true,
        observe: "events",
      },
    );
  }

  /** Create document index row without a file (parent header for grouped uploads). */
  createDocumentIndexMetadata(fd: FormData): Observable<any> {
    return this.http.post<any>(
      `${app_url}/api/v1/efiling/efiling-documents-index/`,
      fd,
    );
  }

  delete_case_documnets_before_final_filing(id: number): Observable<any> {
    return this.http.delete<any>(
      `${app_url}/api/v1/efiling/efiling-documents/${id}/`,
    );
  }

  final_submit_efiling(id: number): Observable<any> {
    var fd = new FormData();
    fd.append("is_draft", "false");
    return this.http.patch<any>(
      `${app_url}/api/v1/efiling/efilings/${id}/`,
      fd,
    );
  }

  update_filing_petitioner_name(id: number, petitionerName: string): Observable<any> {
    const fd = new FormData();
    fd.append("petitioner_name", petitionerName);
    return this.http.patch<any>(`${app_url}/api/v1/efiling/efilings/${id}/`, fd);
  }

  add_case_details_act(fd: FormData) {
    return this.http.post<any>(`${app_url}/api/v1/efiling/efiling-acts/`, fd);
  }

  delete_case_details_act(id: number): Observable<any> {
    return this.http.delete<any>(
      `${app_url}/api/v1/efiling/efiling-acts/${id}/`,
    );
  }

  get_filings_under_scrutiny(params?: { page_size?: number }): Observable<any> {
    let url = `${app_url}/api/v1/efiling/efilings/?is_draft=false&status=NOT_ACCEPTED`;
    if (params?.page_size != null) {
      url += `&page_size=${params.page_size}`;
    }
    return this.http.get<any>(url);
  }
  get_filings(): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efilings/`);
  }
  get_approved_cases(params?: { page_size?: number }): Observable<any> {
    let url = `${app_url}/api/v1/efiling/efilings/?is_draft=false&status=ACCEPTED`;
    if (params?.page_size != null) {
      url += `&page_size=${params.page_size}`;
    }
    return this.http.get<any>(url);
  }

  get_distinct_benches(): Observable<DistinctBenchOption[]> {
    return this.http.get<DistinctBenchOption[]>(
      `${app_url}/api/v1/efiling/benches/distinct/`,
    );
  }

  get_scrutiny_cases(params?: { page_size?: number }): Observable<any> {
    let url = `${app_url}/api/v1/efiling/efilings/?is_draft=false`;
    if (params?.page_size != null) {
      url += `&page_size=${params.page_size}`;
    }
    return this.http.get<any>(url);
  }
  get_filings_under_draft(params?: { page_size?: number }): Observable<any> {
    let url = `${app_url}/api/v1/efiling/efilings/?is_draft=true`;
    if (params?.page_size != null) {
      url += `&page_size=${params.page_size}`;
    }
    return this.http.get<any>(url);
  }

  get_filing_by_id(id: number): Observable<any> {
    console.log(`${app_url}/api/v1/efiling/efilings/${id}/`);
    return this.http.get<any>(`${app_url}/api/v1/efiling/efilings/${id}/`);
  }

  get_filing_by_efiling_id(id: number): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efilings/${id}`);
  }

  submit_approved_filing(id: number, bench?: string): Observable<any> {
    return this.http.post<any>(
      `${app_url}/api/v1/efiling/efilings/${id}/submit-approved/`,
      { bench },
    );
  }

  get_litigant_list_by_filing_id(id: number): Observable<any> {
    console.log(
      `${app_url}/api/v1/efiling/efiling-litigants/?efiling_id=${id}`,
    );
    return this.http.get<any>(
      `${app_url}/api/v1/efiling/efiling-litigants/?efiling_id=${id}`,
    );
  }
  get_case_details_by_filing_id(id: number): Observable<any> {
    console.log(
      `${app_url}/api/v1/efiling/efiling-case-details/?efiling_id=${id}`,
    );
    return this.http.get<any>(
      `${app_url}/api/v1/efiling/efiling-case-details/?efiling_id=${id}`,
    );
  }

  get_acts_by_filing_id(id: number): Observable<any> {
    return this.http.get<any>(
      `${app_url}/api/v1/efiling/efiling-acts/?efiling_id=${id}`,
    );
  }

  get_documents_by_filing_id(id: number): Observable<any> {
    return this.http.get<any>(
      `${app_url}/api/v1/efiling/efiling-documents/?efiling_id=${id}`,
    );
  }

  get_efiling_documents(): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/efiling-documents/`);
  }

  get_document_reviews_by_filing_id(
    id: number,
    isIaOnly?: boolean,
  ): Observable<any> {
    let url = `${app_url}/api/v1/efiling/efiling-documents-index/?efiling_id=${id}`;
    if (isIaOnly === true) {
      url += "&is_ia=true";
    } else if (isIaOnly === false) {
      url += "&is_ia=false";
    }
    return this.http.get<any>(url);
  }

  get_document_scrutiny_history(documentIndexId: number): Observable<any> {
    return this.http.get<any>(
      `${app_url}/api/v1/efiling/efiling-documents-scrutiny-history/?document_index_id=${documentIndexId}`,
    );
  }

  fetch_document_blob(fileUrl: string): Observable<Blob> {
    const candidates = this.buildDocumentUrlCandidates(fileUrl);
    return this.http.get(candidates[0], { responseType: "blob" }).pipe(
      catchError((firstErr) => {
        if (candidates.length < 2) {
          return throwError(() => firstErr);
        }
        return this.http.get(candidates[1], { responseType: "blob" });
      }),
    );
  }

  fetch_document_blob_by_index(documentIndexId: number): Observable<Blob> {
    return this.http.get(
      `${app_url}/api/v1/efiling/efiling-documents-index/${documentIndexId}/stream/`,
      { responseType: "blob" },
    );
  }

  private buildDocumentUrlCandidates(fileUrl: string): string[] {
    const primary = this.resolveDocumentUrl(fileUrl);
    const out = [primary];
    try {
      const u = new URL(primary);
      const parts = u.pathname.split("/");
      if (parts.length >= 4) {
        // /media/efile/<filing>/<docType>/<file>
        const docTypeIdx = parts.length - 2;
        const docType = parts[docTypeIdx] || "";
        const upper = docType.toUpperCase();
        const lower = docType.toLowerCase();
        if (upper && upper !== docType) {
          const p2 = [...parts];
          p2[docTypeIdx] = upper;
          out.push(`${u.origin}${p2.join("/")}`);
        }
        if (lower && lower !== docType) {
          const p3 = [...parts];
          p3[docTypeIdx] = lower;
          out.push(`${u.origin}${p3.join("/")}`);
        }
      }
    } catch {
      // ignore parse issue; keep primary only
    }
    return Array.from(new Set(out));
  }

  private resolveDocumentUrl(fileUrl: string): string {
    const raw = String(fileUrl ?? "").trim();
    if (!raw) return raw;
    if (raw.startsWith("http://") || raw.startsWith("https://")) return raw;
    if (raw.startsWith("/media/")) return `${app_url}${raw}`;
    if (raw.startsWith("media/")) return `${app_url}/${raw}`;
    if (raw.startsWith("/")) return `${app_url}${raw}`;
    return `${app_url}/${raw}`;
  }

  review_document(
    documentIndexId: number,
    payload: FormData | Record<string, any>,
  ): Observable<any> {
    return this.http.patch<any>(
      `${app_url}/api/v1/efiling/efiling-documents-index/${documentIndexId}/`,
      payload,
    );
  }

  replace_document(
    documentId: number,
    file: File,
    documentType?: string,
  ): Observable<any> {
    const fd = new FormData();
    fd.append("final_document", file);
    if (documentType) {
      fd.append("document_type", documentType);
    }
    return this.http.patch<any>(
      `${app_url}/api/v1/efiling/efiling-documents/${documentId}/`,
      fd,
    );
  }

  replace_document_review_item(
    documentIndexId: number,
    file: File,
  ): Observable<any> {
    const fd = new FormData();
    fd.append("file_part_path", file);
    return this.http.patch<any>(
      `${app_url}/api/v1/efiling/efiling-documents-index/${documentIndexId}/`,
      fd,
    );
  }

  get_new_scrutiny_documents(params?: { page_size?: number }): Observable<any> {
    let url = `${app_url}/api/v1/efiling/efiling-documents-index/?is_new_for_scrutiny=true`;
    if (params?.page_size != null) {
      url += `&page_size=${params.page_size}`;
    }
    return this.http.get<any>(url);
  }

  get_file_scrutiny_checklist(caseTypeId: number): Observable<any> {
    return this.http.get<any>(
      `${app_url}/api/v1/efiling/file-scrutiny-checklists/?case_type=${caseTypeId}`,
    );
  }

  get_document_index_master(): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/document-index/`);
  }

  /** Master rows for a case type when building the new-filing upload checklist. */
  get_document_index_for_new_filing(caseTypeId: number): Observable<any> {
    const params = new HttpParams()
      .set("case_type", String(caseTypeId))
      .set("for_new_filing", "true");
    return this.http.get<any>(`${app_url}/api/v1/efiling/document-index/`, {
      params,
    });
  }

  mergePdfs(
    files: File[],
    names?: string[],
    frontPage?: {
      petitionerName: string;
      respondentName: string;
      caseNo: string;
      caseType?: string;
    },
  ): Observable<Blob> {
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f, f.name));
    if (names && names.length === files.length) {
      formData.append("names", JSON.stringify(names));
    }
    if (frontPage) {
      formData.append("petitioner_name", frontPage.petitionerName);
      formData.append("respondent_name", frontPage.respondentName);
      formData.append("case_no", frontPage.caseNo);
      if (frontPage.caseType) formData.append("case_type", frontPage.caseType);
    }
    return this.http.post(`${app_url}/api/v1/efiling/merge-pdfs/`, formData, {
      responseType: "blob",
    });
  }

  post_ia_filing(payload: {
    e_filing: number;
    e_filing_number: string;
    ia_text: string;
    status?: string;
  }): Observable<any> {
    const body = { status: "UNDER_SCRUTINY", ...payload };
    return this.http.post<any>(`${app_url}/api/v1/efiling/ias/`, body);
  }

  get_ias(): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/ias/`);
  }

  get_ias_by_efiling_id(efilingId: number): Observable<any> {
    return this.http.get<any>(
      `${app_url}/api/v1/efiling/ias/?e_filing=${efilingId}`,
    );
  }

  get_ia_by_id(id: number): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/ias/${id}/`);
  }

  verify_ia(iaId: number): Observable<any> {
    return this.http.patch<any>(`${app_url}/api/v1/efiling/ias/${iaId}/`, {
      status: "ACCEPTED",
    });
  }

  get_ia_acts_by_ia_id(iaId: number): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/efiling/ia-acts/?ia=${iaId}`);
  }

  get_notifications(role: "advocate" | "scrutiny_officer"): Observable<any[]> {
    return this.http.get<any[]>(
      `${app_url}/api/v1/efiling/notifications/?role=${role}`,
    );
  }
}
