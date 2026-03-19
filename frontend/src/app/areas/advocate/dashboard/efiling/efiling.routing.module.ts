import { Routes } from '@angular/router';

export const EfilingRoutes: Routes = [
  {
    path: 'new-filing',
    loadComponent: () => import('./new-filing/new-filing').then((c) => c.NewFiling),
  },
  {
    path: 'draft-filings',
    loadChildren: () =>
      import('./draft-filings/draft-filing.routing').then((r) => r.DraftFilingRoutes),
  },
  {
    path: 'pending-cases',
    loadComponent: () => import('./pending-cases/pending-cases').then((c) => c.PendingCases),
  },
  {
    path: 'pending-scrutiny',
    loadChildren: () =>
      import('./cases-scrutiny/cases-scrutiny-routing-module').then((c) => c.routes),
  },
];
