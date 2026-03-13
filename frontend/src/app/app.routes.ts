import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'sda',
    loadComponent: () => import('./landing/landing').then((m) => m.Landing),
  },
  {
    path: '',
    loadChildren: () => import('./areas/advocate/advocate-routing-module').then((m) => m.routes),
  },
];
