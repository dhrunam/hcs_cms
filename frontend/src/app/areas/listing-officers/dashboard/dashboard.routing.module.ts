import { Routes } from '@angular/router';

export const ListingOfficerDashboardRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./dashboard').then((c) => c.ListingOfficerDashboard),
    children: [
      {
        path: '',
        redirectTo: 'generate-cause-list',
        pathMatch: 'full',
      },
      {
        path: 'home',
        redirectTo: 'generate-cause-list',
        pathMatch: 'full',
      },
      {
        path: 'listed-cases',
        loadComponent: () =>
          import('./listed-cases/listed-cases').then((c) => c.ListedCasesPage),
        title: 'Listed Cases | CMS',
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

