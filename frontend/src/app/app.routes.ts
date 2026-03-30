import { Routes } from '@angular/router';
import { AuthRedirectComponent } from './auth-redirect.component';

export const routes: Routes = [
  {
    path: 'auth/redirect',
    component: AuthRedirectComponent,
  },
  {
    path: 'user/login',
    loadComponent: () => import('./areas/auth/login/login').then((m) => m.Login),
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
    path: 'listing-officers',
    loadChildren: () =>
      import('./areas/listing-officers/listing-officers-routing-module').then(
        (m) => m.ListingOfficerRoutes,
      ),
  },
  {
    path: 'judges',
    loadChildren: () =>
      import('./areas/judges/judges-routing-module').then((m) => m.JudgeRoutes),
  },
  {
    path: '',
    redirectTo: 'user/login',
    pathMatch: 'full',
  },
];
