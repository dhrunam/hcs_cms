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
  txn_id?: string;
  reference_no?: string;
  amount?: string;
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
}
