import { Routes } from '@angular/router';
import { AuthRedirectComponent } from './auth-redirect.component';

export const routes: Routes = [
  {
    path: 'auth/redirect',
    component: AuthRedirectComponent,
  },
  {
    path: 'advocate',
    loadChildren: () =>
      import('./areas/advocate/advocate-routing-module').then((m) => m.AdvocateRoutes),
  },
];
