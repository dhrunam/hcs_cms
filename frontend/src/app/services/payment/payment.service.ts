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
  application?: string;
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

@Injectable({ providedIn: "root" })
export class PaymentService {
  constructor(private http: HttpClient) {}

  initiate(payload: {
    amount: string | number;
    application: number | string;
    e_filing_number: string;
    payment_type?: string;
    source?: "new_filing" | "draft";
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

  submitOffline(payload: {
    application: string | number;
    txn_id: string;
    court_fees: string | number;
    payment_date: string;
    payment_type?: string;
    bank_receipt: File;
  }): Observable<any> {
    const fd = new FormData();
    fd.append("application", String(payload.application));
    fd.append("txn_id", String(payload.txn_id || "").trim());
    fd.append("court_fees", String(payload.court_fees || "").trim());
    fd.append("payment_date", String(payload.payment_date || "").trim());
    fd.append("payment_type", payload.payment_type || "Court Fees");
    fd.append("bank_receipt", payload.bank_receipt);
    return this.http.post<any>(`${app_url}/api/payment/offline/`, fd);
  }
}
