import { Routes } from '@angular/router';

export const StenoDashboardRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./dashboard').then((c) => c.StenoDashboard),
    children: [
      {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full',
      },
      {
        path: 'home',
        loadComponent: () =>
          import('./home/home').then((m) => m.StenoHomePage),
        title: 'Steno | Queue',
      },
      {
        path: 'published-cases',
        loadComponent: () =>
          import('./published-cases/published-cases').then((m) => m.PublishedCases),
        title: 'Steno | Queue',
      },
    ],
  },
];
