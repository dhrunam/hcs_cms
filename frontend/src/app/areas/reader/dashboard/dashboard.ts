import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterModule } from '@angular/router';

@Component({
  selector: 'app-reader-dashboard',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterModule],
  template: `
    <div class="d-flex h-100 reader-dashboard">
      <div class="sidebar bg-dark text-white p-3 shadow" style="width: 250px;">
        <h5 class="mb-4 text-center py-2 border-bottom border-secondary">Reader Module</h5>
        <ul class="nav flex-column">
          <li class="nav-item">
            <a class="nav-link text-white d-flex align-items-center gap-2" routerLink="./registered-cases" routerLinkActive="active">
              <i class="fa-solid fa-folder-open"></i> Registered Cases
            </a>
          </li>
          <li class="nav-item mt-auto pt-4">
            <a class="nav-link text-danger d-flex align-items-center gap-2" routerLink="/auth/logout">
              <i class="fa-solid fa-right-from-bracket"></i> Logout
            </a>
          </li>
        </ul>
      </div>
      <div class="flex-grow-1 overflow-auto bg-light d-flex flex-column">
        <header class="bg-white border-bottom p-3 d-flex justify-content-between align-items-center shadow-sm">
          <h5 class="mb-0 text-primary fw-bold">Case Management System</h5>
          <div class="user-profile small text-muted">
             Role: <span class="badge bg-info text-dark">Reader</span>
          </div>
        </header>
        <main class="p-4 flex-grow-1">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; height: 100vh; }
    .reader-dashboard { font-family: 'Inter', sans-serif; }
    .nav-link { padding: 0.75rem 1rem; border-radius: 6px; transition: all 0.2s; }
    .nav-link:hover { background: rgba(255,255,255,0.1); }
    .nav-link.active { background: #0d6efd; color: white !important; font-weight: 600; }
  `]
})
export class ReaderDashboard {}
