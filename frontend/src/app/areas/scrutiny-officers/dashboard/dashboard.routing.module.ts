import { Routes } from '@angular/router';

export const ScrutinyOfficerDashboardRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./dashboard').then((c) => c.ScrutinyOfficerDashboard),
    children: [
      {
        path: 'home',
        loadComponent: () => import('./home/home').then((c) => c.ScrutinyOfficerHome),
        title: 'Scrutiny Officer Dashboard | CMS',
      },
      {
        path: 'filed-cases',
        loadChildren: () =>
          import('./filed-cases/filed-cases.routing.module').then((m) => m.FiledCasesRoutes),
        title: 'Filed Cases | CMS',
      },
      {
        path: 'grant-case-access',
        loadComponent: () =>
          import('./grant-case-access/grant-case-access').then((c) => c.GrantCaseAccess),
        title: 'Grant Case Access | CMS',
      },
    ],
  },
];
