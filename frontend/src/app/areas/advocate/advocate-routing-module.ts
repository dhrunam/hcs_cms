import { Routes } from '@angular/router';

export const AdvocateRoutes: Routes = [
  { path: '', redirectTo: '/advocate/dashboard', pathMatch: 'full'},
  { path: 'dashboard', loadChildren: () => import('./dashboard/dashboard.routing.module').then(r => r.DashboardRoutes)},
];
