import { Routes } from '@angular/router';

export const ListingOfficerRoutes: Routes = [
  { path: '', redirectTo: '/listing-officers/dashboard/home', pathMatch: 'full' },
  {
    path: 'dashboard',
    loadChildren: () =>
      import('./dashboard/dashboard.routing.module').then((m) => m.ListingOfficerDashboardRoutes),
  },
];

