import { Component, HostListener, inject, signal } from '@angular/core';
import { NgClass } from '@angular/common';
import {
  ActivatedRoute,
  NavigationEnd,
  Router,
  RouterLink,
  RouterLinkActive,
  RouterOutlet,
} from '@angular/router';
import { filter } from 'rxjs';
import { AuthService } from '../auth.service';
import {
  DASHBOARD_AREA_CONFIG,
  type DashboardAreaKey,
  type ShellAreaConfig,
} from './dashboard-nav.config';

@Component({
  selector: 'app-dashboard-shell',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, NgClass],
  templateUrl: './dashboard-shell.component.html',
  styleUrl: './dashboard-shell.component.css',
})
export class DashboardShellComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  readonly mobileNavOpen = signal(false);
  readonly sidebarCollapsed = signal(false);
  readonly profileMenuOpen = signal(false);

  /** Collapsible nav sections (e.g. Management) — key = item label */
  readonly expandedNavSections = signal<Record<string, boolean>>({});

  readonly shellConfig: ShellAreaConfig | null;

  constructor() {
    const key = this.route.snapshot.data['areaKey'] as DashboardAreaKey | undefined;
    this.shellConfig =
      key && DASHBOARD_AREA_CONFIG[key] ? DASHBOARD_AREA_CONFIG[key] : null;

    if (this.shellConfig?.areaKey === 'superadmin') {
      this.expandedNavSections.set({ Management: true });
    }
    this.router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe(() => {
        if (this.router.url.includes('/admin')) {
          this.expandedNavSections.update((m) => ({ ...m, Management: true }));
        }
      });
  }

  toggleNavSection(label: string): void {
    this.expandedNavSections.update((m) => ({ ...m, [label]: !m[label] }));
  }

  isNavExpanded(label: string): boolean {
    return this.expandedNavSections()[label] ?? false;
  }

  /** Role line from DB-backed profile groups / sessionStorage / JWT */
  get userRoleLine(): string {
    return this.auth.getUserRoleDisplayLabel();
  }

  /** Shown next to profile avatar */
  get userLabel(): string {
    return this.auth.getUserDisplayLabel();
  }

  get userInitials(): string {
    const raw = this.auth.getUserDisplayNameRaw().trim();
    const parts = raw.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return raw.slice(0, 2).toUpperCase() || '?';
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const el = event.target as HTMLElement | null;
    if (el?.closest('[data-profile-dropdown]')) {
      return;
    }
    this.profileMenuOpen.set(false);
  }

  toggleMobileNav(): void {
    this.mobileNavOpen.update((v) => !v);
  }

  closeMobileNav(): void {
    this.mobileNavOpen.set(false);
  }

  toggleSidebarCollapse(): void {
    this.sidebarCollapsed.update((v) => !v);
  }

  toggleProfileMenu(event: MouseEvent): void {
    event.stopPropagation();
    this.profileMenuOpen.update((v) => !v);
  }

  viewProfile(): void {
    const key = this.shellConfig?.areaKey;
    if (!key) {
      return;
    }
    void this.router.navigate([key, 'dashboard', 'profile']);
    this.profileMenuOpen.set(false);
    this.closeMobileNav();
  }

  async logout(): Promise<void> {
    this.profileMenuOpen.set(false);
    await this.auth.logout();
    await this.router.navigate(['/user/login']);
  }
}
