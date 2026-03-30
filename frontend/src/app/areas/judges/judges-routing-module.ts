import { Routes } from '@angular/router';

export const JudgeRoutes: Routes = [
  { path: '', redirectTo: '/judges/dashboard/home', pathMatch: 'full' },
  {
    path: 'dashboard',
    loadChildren: () =>
      import('./dashboard/dashboard.routing.module').then((m) => m.JudgeDashboardRoutes),
  },
];

