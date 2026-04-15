import { Component, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-profile-page',
  standalone: true,
  imports: [RouterLink],
  template: `
    <div class="relative overflow-hidden px-4 py-8 sm:px-6 lg:px-10">
      <div
        class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_10%_-20%,rgba(30,58,95,0.08),transparent),radial-gradient(ellipse_60%_40%_at_90%_100%,rgba(59,130,246,0.06),transparent)]"
        aria-hidden="true"
      ></div>

      <div class="relative mx-auto max-w-3xl">
        <div
          class="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-xl shadow-slate-200/40 ring-1 ring-slate-100"
        >
          <div
            class="h-28 bg-gradient-to-r from-[#1e3a5f] via-[#2d5a8a] to-[#1e40af] sm:h-32"
            aria-hidden="true"
          ></div>
          <div class="relative px-6 pb-8 pt-0 sm:px-8">
            <div
              class="-mt-14 flex h-28 w-28 items-center justify-center rounded-2xl border-4 border-white bg-gradient-to-br from-slate-100 to-slate-200 text-3xl font-bold text-[#1e3a5f] shadow-lg sm:h-32 sm:w-32 sm:text-4xl"
            >
              {{ initials }}
            </div>
            <h1 class="font-display mt-4 text-2xl font-bold tracking-tight text-slate-900">{{ heading }}</h1>
            <p class="mt-1 text-sm text-slate-500">Account details from your eFiling session</p>

            <dl class="mt-8 grid gap-4 sm:grid-cols-2">
              <div
                class="rounded-xl border border-slate-100 bg-slate-50/80 p-4 transition hover:border-[#1e3a5f]/20 hover:shadow-md"
              >
                <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Display name</dt>
                <dd class="mt-1 font-medium text-slate-800">{{ displayName }}</dd>
              </div>
              <div
                class="rounded-xl border border-slate-100 bg-slate-50/80 p-4 transition hover:border-[#1e3a5f]/20 hover:shadow-md"
              >
                <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Email</dt>
                <dd class="mt-1 font-medium text-slate-800">{{ email }}</dd>
              </div>
              <div
                class="rounded-xl border border-slate-100 bg-slate-50/80 p-4 transition hover:border-[#1e3a5f]/20 hover:shadow-md sm:col-span-2"
              >
                <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Roles</dt>
                <dd class="mt-1 font-medium text-slate-800">{{ rolesLine }}</dd>
              </div>
            </dl>

            <p class="mt-8 text-sm text-slate-500">
              To change your password or official records, contact the court office or use future self-service
              tools when available.
            </p>
          </div>
        </div>

        <p class="mt-6 text-center">
          <a
            [routerLink]="dashboardHomeLink"
            class="inline-flex items-center gap-2 text-sm font-semibold text-[#2d5a8a] hover:underline"
          >
            ← Back to dashboard
          </a>
        </p>
      </div>
    </div>
  `,
})
export class ProfilePageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  /** e.g. `['advocate','dashboard','home']`; `/admin/*` maps to `superadmin` home. */
  get dashboardHomeLink(): string[] {
    const seg = this.router.url.split('?')[0].split('/').filter(Boolean)[0] ?? '';
    const prefix = seg === 'admin' ? 'superadmin' : seg;
    return [prefix, 'dashboard', 'home'];
  }

  get heading(): string {
    return (this.route.snapshot.data['title'] as string) || 'Profile';
  }

  get displayName(): string {
    return this.auth.getSessionProfile()?.displayName?.trim() || '—';
  }

  get email(): string {
    return this.auth.getSessionProfile()?.email?.trim() || '—';
  }

  get rolesLine(): string {
    const g = this.auth.getUserGroups();
    return g.length ? g.join(', ') : '—';
  }

  get initials(): string {
    const p = this.auth.getSessionProfile();
    const raw = (p?.displayName || p?.email || '?').trim();
    const parts = raw.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return raw.slice(0, 2).toUpperCase() || '?';
  }
}
