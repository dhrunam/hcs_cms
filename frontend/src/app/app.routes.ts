import { Routes } from '@angular/router';

export const routes: Routes = [
  // {
  //   path: '',
  //   redirectTo: '/advocate/dashboard/home',
  // },
  {
    path: 'advocate',
    loadChildren: () =>
      import('./areas/advocate/advocate-routing-module').then((m) => m.AdvocateRoutes),
  },
];
