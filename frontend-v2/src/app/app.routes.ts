import { Routes } from '@angular/router';
import { authGuard } from './core/auth.guard';
import { superAdminGuard } from './core/super-admin.guard';
import type { DashboardAreaKey } from './shell/dashboard-nav.config';

function roleDashboardRoute(path: string, areaKey: DashboardAreaKey, homeTitle: string) {
  return {
    path,
    loadComponent: () =>
      import('./shell/dashboard-shell.component').then((m) => m.DashboardShellComponent),
    canMatch: [authGuard],
    data: { areaKey },
    children: [
      { path: '', pathMatch: 'full' as const, redirectTo: 'dashboard/home' },
      {
        path: 'dashboard/home',
        loadComponent: () =>
          import('./shell/dashboard-page.component').then((m) => m.DashboardPageComponent),
        data: { title: homeTitle },
      },
      {
        path: 'dashboard/profile',
        loadComponent: () =>
          import('./shell/profile-page.component').then((m) => m.ProfilePageComponent),
        data: { title: 'Your profile' },
      },
    ],
  };
}

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'user/login' },
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
    path: 'user/register/advocate',
    loadComponent: () =>
      import('./areas/auth/register-advocate/register-advocate').then((m) => m.RegisterAdvocate),
  },
  {
    path: 'user/register/party',
    loadComponent: () =>
      import('./areas/auth/register-party/register-party').then((m) => m.RegisterParty),
  },
  {
    path: 'user/verify-email',
    loadComponent: () =>
      import('./areas/auth/verify-email/verify-email').then((m) => m.VerifyEmail),
  },
  roleDashboardRoute('superadmin', 'superadmin', 'Super Admin · Home'),
  {
    path: 'admin',
    loadComponent: () =>
      import('./shell/dashboard-shell.component').then((m) => m.DashboardShellComponent),
    canMatch: [authGuard, superAdminGuard],
    data: { areaKey: 'superadmin' satisfies DashboardAreaKey },
    children: [
      { path: '', pathMatch: 'full' as const, redirectTo: 'users' },
      {
        path: 'users',
        loadComponent: () =>
          import('./modules/admin/components/users/users.component').then((m) => m.UsersComponent),
        data: { title: 'Users' },
      },
      {
        path: 'roles',
        loadComponent: () =>
          import('./modules/admin/components/roles/roles.component').then((m) => m.RolesComponent),
        data: { title: 'Roles' },
      },
      {
        path: 'permissions',
        loadComponent: () =>
          import('./modules/admin/components/permissions/permissions.component').then(
            (m) => m.PermissionsComponent,
          ),
        data: { title: 'Permissions' },
      },
    ],
  },
  roleDashboardRoute('advocate', 'advocate', 'Advocate · Home'),
  roleDashboardRoute('party', 'party', 'Party in person · Home'),
  roleDashboardRoute('judges', 'judges', 'Judge · Home'),
  roleDashboardRoute('reader', 'reader', 'Reader · Home'),
  roleDashboardRoute('listing-officers', 'listing-officers', 'Listing officer · Home'),
  roleDashboardRoute('scrutiny-officers', 'scrutiny-officers', 'Scrutiny officer · Home'),
  roleDashboardRoute('steno', 'steno', 'Steno · Home'),
  { path: '**', redirectTo: 'user/login' },
];
