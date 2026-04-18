import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";

import { app_url } from "../../environment";

export interface PaymentInitiateResponse {
  method: "POST";
  action: string;
  fields: Record<string, string>;
}

export interface PaymentLatestResponse {
  id?: number;
  application?: string;
  payment_type?: string;
  payment_mode?: string;
  txn_id?: string;
  reference_no?: string;
  amount?: string;
  court_fees?: string;
  payment_date?: string;
  bank_receipt?: string | null;
  status?: string;
  message?: string;
  payment_datetime?: string;
  paid_at?: string;
}

export interface PaymentTransactionsListResponse {
  results: PaymentLatestResponse[];
}

@Injectable({ providedIn: "root" })
export class PaymentService {
  constructor(private http: HttpClient) {}

  initiate(payload: {
    amount: string | number;
    application: number | string;
    e_filing_number: string;
    payment_type?: string;
    source?: "new_filing" | "draft" | "ia_filing" | "document_filing";
    /** Existing-case document filing: fee tied to this EfilingDocuments row after upload. */
    efiling_document_id?: number;
  }): Observable<PaymentInitiateResponse> {
    return this.http.post<PaymentInitiateResponse>(
      `${app_url}/api/payment/initiate/`,
      payload,
    );
  }

  latest(application: string | number): Observable<PaymentLatestResponse> {
    return this.http.get<PaymentLatestResponse>(
      `${app_url}/api/payment/latest/?application=${application}`,
    );
  }

  list(application: string | number): Observable<PaymentTransactionsListResponse> {
    return this.http.get<PaymentTransactionsListResponse>(
      `${app_url}/api/payment/transactions/?application=${application}`,
    );
  }

  submitOffline(payload: {
    application: string | number;
    txn_id: string;
    court_fees: string | number;
    payment_date: string;
    payment_type?: string;
    e_filing_number?: string;
    bank_receipt: File;
    efiling_document_id?: number;
    source?: string;
  }): Observable<any> {
    const fd = new FormData();
    fd.append("application", String(payload.application));
    fd.append("txn_id", String(payload.txn_id || "").trim());
    fd.append("court_fees", String(payload.court_fees || "").trim());
    fd.append("payment_date", String(payload.payment_date || "").trim());
    fd.append("payment_type", payload.payment_type || "Court Fees");
    if (payload.e_filing_number) {
      fd.append("e_filing_number", String(payload.e_filing_number).trim());
    }
    if (payload.efiling_document_id != null) {
      fd.append("efiling_document_id", String(payload.efiling_document_id));
    }
    if (payload.source) {
      fd.append("source", payload.source);
    }
    fd.append("bank_receipt", payload.bank_receipt);
    return this.http.post<any>(`${app_url}/api/payment/offline/`, fd);
  }
}
