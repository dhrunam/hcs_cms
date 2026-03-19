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
  {
    path: 'scrutiny-officers',
    loadChildren: () =>
      import('./areas/scrutiny-officers/scrutiny-officers-routing-module').then(
        (m) => m.ScrutinyOfficerRoutes,
      ),
  },
  {
    path: '',
    redirectTo: 'advocate',
    pathMatch: 'full',
  },
];
