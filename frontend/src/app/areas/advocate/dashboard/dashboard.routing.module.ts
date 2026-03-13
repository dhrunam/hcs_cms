import { Routes } from '@angular/router';

export const DashboardRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./dashboard').then(c => c.Dashboard ),
    children: [
        { path: '', loadComponent: () => import('./home/home').then(c => c.Home)},
        { path: 'efiling', loadChildren: () => import('./efiling/efiling.routing.module').then(r => r.EfilingRoutes ) },
    ],
  },
];
