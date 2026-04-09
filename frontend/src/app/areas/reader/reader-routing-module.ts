import { Routes } from '@angular/router';

export const ReaderRoutes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./dashboard/dashboard').then((m) => m.ReaderDashboard),
    children: [
      {
        path: '',
        redirectTo: 'registered-cases',
        pathMatch: 'full',
      },
      {
        path: 'registered-cases',
        loadComponent: () =>
          import('./dashboard/registered-cases/registered-cases').then(
            (m) => m.RegisteredCasesPage,
          ),
        title: 'Reader | Registered Cases',
      },
      {
        path: 'case/:id',
        loadComponent: () =>
          import('./dashboard/case-summary/case-summary').then(
            (m) => m.ReaderCaseSummaryPage,
          ),
        title: 'Reader | Case Summary',
      },
      {
        path: 'approved-cases',
        loadComponent: () =>
          import('./dashboard/approved-cases/approved-cases').then(
            (m) => m.ReaderApprovedCasesPage,
          ),
        title: 'Reader | Approved Cases',
      },
      {
        path: 'daily-proceedings',
        loadComponent: () =>
          import('./dashboard/daily-proceedings/daily-proceedings').then(
            (m) => m.ReaderDailyProceedingsPage,
          ),
        title: 'Reader | Daily Proceedings',
      },
    ],
  },
];
