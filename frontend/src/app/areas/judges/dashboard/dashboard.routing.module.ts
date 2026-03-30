import { Routes } from '@angular/router';

export const JudgeDashboardRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./dashboard').then((c) => c.JudgeDashboard),
    children: [
      {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full',
      },
      {
        path: 'home',
        loadComponent: () =>
          import('./home/home').then((c) => c.JudgePendingCasesPage),
        title: 'Judge Courtroom | CMS',
      },
      {
        path: 'courtroom/:id',
        loadComponent: () =>
          import('./courtroom/courtroom').then((c) => c.JudgeCourtroomPage),
        title: 'Courtroom | CMS',
      },
    ],
  },
];

