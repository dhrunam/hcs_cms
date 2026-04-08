import { Routes } from '@angular/router';

export const StenoRoutes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard/home',
    pathMatch: 'full',
  },
  {
    path: 'dashboard/home',
    loadComponent: () =>
      import('./dashboard/home/home').then((m) => m.StenoHomePage),
    title: 'Steno | Queue',
  },
];

