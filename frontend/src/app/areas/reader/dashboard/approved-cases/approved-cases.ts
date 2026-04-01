import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { BenchConfiguration, ReaderService } from '../../../../services/reader/reader.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-reader-approved-cases',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3 border-bottom-0">
        <h5 class="mb-0 fw-bold text-primary">Approved Cases from Judges</h5>
        <p class="text-muted mb-0 small">Select a bench to see cases approved by judges that are ready for final listing.</p>
      </div>
      <div class="card-body">
        <div class="row g-3 mb-4 p-3 bg-light rounded shadow-sm mx-0">
          <div class="col-md-5">
            <label class="form-label small fw-bold">Select Bench</label>
            <select class="form-select border-0 shadow-sm" [(ngModel)]="benchKey">
              <option *ngFor="let bench of benchConfigurations" [value]="bench.bench_key">{{ bench.label }}</option>
            </select>
          </div>
          <div class="col-md-5">
            <label class="form-label small fw-bold">Forwarded For Date</label>
            <input type="date" class="form-control border-0 shadow-sm" [(ngModel)]="forwardedForDate" />
          </div>
          <div class="col-md-2 d-flex align-items-end">
            <button class="btn btn-primary w-100 shadow-sm" (click)="search()" [disabled]="isLoading">
               <i class="fa-solid fa-magnifying-glass"></i> Search
            </button>
          </div>
        </div>

        <div *ngIf="isLoading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="text-muted mt-2">Loading approved cases...</p>
        </div>

        <div *ngIf="!isLoading && cases.length > 0">
          <div class="table-responsive rounded shadow-sm border">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th class="ps-3">Case Number</th>
                  <th>E-Filing No.</th>
                  <th>Petitioner</th>
                  <th>Status</th>
                  <th class="text-end pe-3">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let c of cases">
                  <td class="ps-3">
                    <div class="fw-semibold">{{ c.case_number || '-' }}</div>
                  </td>
                  <td>{{ c.e_filing_number || '-' }}</td>
                  <td>{{ c.petitioner_name || '-' }}</td>
                  <td>
                    <span class="badge bg-success rounded-pill px-3">Approved</span>
                  </td>
                  <td class="text-end pe-3">
                    <button class="btn btn-outline-primary btn-sm rounded-pill px-3" (click)="openCase(c.id)">
                      Assign Date
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div *ngIf="!isLoading && cases.length === 0 && searched" class="text-center py-5 border rounded bg-white mt-3 shadow-sm">
           <i class="fa-solid fa-folder-open text-muted fs-1 mb-3"></i>
           <p class="text-muted mb-0">No approved cases found for this bench and date.</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .card { border-radius: 12px; }
    .table th { font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .nav-link { cursor: pointer; }
    tr:hover { background-color: rgba(13, 110, 253, 0.02); }
  `]
})
export class ReaderApprovedCasesPage implements OnInit {
  benchKey = '';
  forwardedForDate = new Date().toISOString().slice(0, 10);
  
  isLoading = false;
  searched = false;
  cases: any[] = [];
  benchConfigurations: BenchConfiguration[] = [];

  constructor(private readerService: ReaderService, private router: Router) {}

  ngOnInit(): void {
    this.readerService.getBenchConfigurations({ accessible_only: true }).subscribe({
      next: (resp) => {
        this.benchConfigurations = (resp?.items ?? []).filter((item) => item.is_forward_target);
        this.benchKey = this.benchConfigurations[0]?.bench_key || '';
      },
      error: () => {
        this.benchConfigurations = [];
      },
    });
  }

  search(): void {
    if (!this.benchKey) {
      Swal.fire({ title: 'Bench Required', text: 'No bench is available for this reader.', icon: 'warning' });
      return;
    }
    this.isLoading = true;
    this.searched = false;
    this.readerService.getApprovedCases({ bench_key: this.benchKey, forwarded_for_date: this.forwardedForDate }).subscribe({
      next: (resp) => {
        this.cases = resp.results;
        this.isLoading = false;
        this.searched = true;
      },
      error: () => {
        this.isLoading = false;
        this.searched = true;
        Swal.fire({ title: 'Error', text: 'Failed to fetch cases.', icon: 'error' });
      }
    });
  }

  openCase(id: number): void {
    this.router.navigate(['/reader/dashboard/case', id]);
  }
}
