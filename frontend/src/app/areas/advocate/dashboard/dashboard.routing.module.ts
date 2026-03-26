import { Routes } from '@angular/router';

export const DashboardRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./dashboard').then((c) => c.Dashboard),
    children: [
      {
        path: 'home',
        loadComponent: () => import('./home/home').then((c) => c.Home),
        title: 'Dashboard | CMS',
      },
      {
        path: 'efiling',
        loadChildren: () => import('./efiling/efiling.routing.module').then((r) => r.EfilingRoutes),
        title: 'New Filing | CMS',
      },
      {
        path: 'cause-list',
        loadComponent: () => import('./cause-list/cause-list').then((c) => c.CauseListPage),
        title: 'Cause List | CMS',
      },
    ],
  },
];
