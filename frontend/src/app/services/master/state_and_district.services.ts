import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { app_url } from '../../environment';
import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class StateAndDistrictService {
  constructor(private http: HttpClient) {}

  get_states(): Observable<any> {
    return this.http.get<any>(`${app_url}/api/v1/master/states/`);
  }
}
