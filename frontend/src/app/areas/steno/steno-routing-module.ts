import { Routes } from '@angular/router';

export const StenoRoutes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },
  {
    path: 'dashboard',
    loadChildren: () =>
      import('./dashboard/dashboard.routing.module').then(
        (m) => m.StenoDashboardRoutes,
      ),
  },
];

