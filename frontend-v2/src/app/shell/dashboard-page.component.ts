import { Component } from '@angular/core';

/** Dashboard home — layout aligned with CMS case management workspace pattern. */
@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  template: `
    <div class="min-h-full px-4 py-8 sm:px-8 lg:px-10">
      <div class="mx-auto max-w-[1600px]">
        <p class="text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-slate-500">Current view</p>
        <h1 class="font-display mt-2 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Dashboard</h1>
        <div class="mt-4 h-px w-full max-w-2xl bg-slate-200" aria-hidden="true"></div>

        <div class="mt-10 grid gap-6 lg:grid-cols-3">
          @for (card of cards; track card.title) {
            <section
              class="rounded-xl border border-slate-200/90 bg-white p-6 shadow-sm transition-shadow duration-200 hover:shadow-md"
            >
              <h2 class="text-base font-semibold text-slate-900">{{ card.title }}</h2>
              <p class="mt-4 text-sm leading-relaxed text-slate-500">
                {{ card.body }}
              </p>
            </section>
          }
        </div>
      </div>
    </div>
  `,
})
export class DashboardPageComponent {
  readonly cards = [
    {
      title: 'Summary',
      body:
        'Key metrics and at-a-glance status for your workspace will appear here once connected to live data.',
    },
    {
      title: 'Recent activity',
      body:
        'A chronological feed of filings, orders, and system events relevant to your role will be listed in this panel.',
    },
    {
      title: 'Actions',
      body:
        'Shortcuts to common tasks—new filing, scheduling, and document uploads—will be available here.',
    },
  ] as const;
}
