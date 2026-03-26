import { Routes } from '@angular/router';

export const ListingOfficerDashboardRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./dashboard').then((c) => c.ListingOfficerDashboard),
    children: [
      {
        path: '',
        redirectTo: 'assign-cases',
        pathMatch: 'full',
      },
      {
        path: 'home',
        redirectTo: 'assign-cases',
        pathMatch: 'full',
      },
      {
        path: 'assign-cases',
        loadComponent: () =>
          import('./registered-cases/registered-cases').then((c) => c.RegisteredCasesPage),
        title: 'Registered Cases | CMS',
      },
      {
        path: 'case/:id',
        loadComponent: () =>
          import('./case-summary/case-summary').then((c) => c.ListingCaseSummaryPage),
        title: 'Case Summary | CMS',
      },
      {
        path: 'generate-cause-list',
        loadComponent: () => import('./home/home').then((c) => c.ListingOfficerHome),
        title: 'Cause List Generator | CMS',
      },
    ],
  },
];

