import { Routes } from '@angular/router';
import { AuthRedirectComponent } from './auth-redirect.component';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  {
    path: '',
    component: AuthRedirectComponent,
    pathMatch: 'full',
  },
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
    canMatch: [authGuard],
    loadChildren: () =>
      import('./areas/advocate/advocate-routing-module').then((m) => m.AdvocateRoutes),
  },
  {
    path: 'scrutiny-officers',
    canMatch: [authGuard],
    loadChildren: () =>
      import('./areas/scrutiny-officers/scrutiny-officers-routing-module').then(
        (m) => m.ScrutinyOfficerRoutes,
      ),
  },
  {
    path: 'listing-officers',
    canMatch: [authGuard],
    loadChildren: () =>
      import('./areas/listing-officers/listing-officers-routing-module').then(
        (m) => m.ListingOfficerRoutes,
      ),
  },
  {
    path: 'judges',
    canMatch: [authGuard],
    loadChildren: () =>
      import('./areas/judges/judges-routing-module').then((m) => m.JudgeRoutes),
  },
  {
    path: 'reader',
    canMatch: [authGuard],
    loadChildren: () =>
      import('./areas/reader/reader-routing-module').then((m) => m.ReaderRoutes),
  },
];
