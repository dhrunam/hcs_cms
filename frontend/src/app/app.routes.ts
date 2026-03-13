import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'advocate',
    loadChildren: () => import('./areas/advocate/advocate-routing-module').then(m => m.AdvocateRoutes),
  },
];
