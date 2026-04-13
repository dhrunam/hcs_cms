import { Routes } from '@angular/router';
import { AuthRedirectComponent } from './auth-redirect.component';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'auth/redirect',
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
    path: 'user/register',
    loadComponent: () =>
      import('./areas/auth/register-hub/register-hub').then((m) => m.RegisterHub),
  },
  {
    path: 'user/register/party',
    loadComponent: () =>
      import('./areas/auth/register-party/register-party').then((m) => m.RegisterParty),
  },
  {
    path: 'user/register/advocate',
    loadComponent: () =>
      import('./areas/auth/register-advocate/register-advocate').then((m) => m.RegisterAdvocate),
  },
  {
    path: 'user/verify-email',
    loadComponent: () =>
      import('./areas/auth/verify-email/verify-email').then((m) => m.VerifyEmail),
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
  {
    path: 'steno',
    canMatch: [authGuard],
    loadChildren: () =>
      import('./areas/steno/steno-routing-module').then((m) => m.StenoRoutes),
  },
];
