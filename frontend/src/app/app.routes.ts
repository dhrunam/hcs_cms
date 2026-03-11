import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'cases',
    pathMatch: 'full',
  },
  {
    path: 'auth/callback',
    loadComponent: () =>
      import('./core/auth/auth-callback.component').then(
        (m) => m.AuthCallbackComponent,
      ),
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login/login.component').then(
        (m) => m.LoginComponent,
      ),
  },
  {
    path: 'cases',
    loadComponent: () =>
      import('./features/cases/cases-list/cases-list.component').then(
        (m) => m.CasesListComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: '**',
    redirectTo: 'cases',
  },
];
