import { Routes } from '@angular/router';

export const ScrutinyOfficerRoutes: Routes = [
  { path: '', redirectTo: '/scrutiny-officers/dashboard/home', pathMatch: 'full' },
  {
    path: 'dashboard',
    loadChildren: () =>
      import('./dashboard/dashboard.routing.module').then((m) => m.ScrutinyOfficerDashboardRoutes),
  },
];
