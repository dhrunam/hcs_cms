import { Routes } from '@angular/router';

export const FiledCasesRoutes: Routes = [
  { path: '', redirectTo: 'view', pathMatch: 'full' },
  {
    path: '',
    loadComponent: () => import('./filed-cases').then((c) => c.FiledCases),
    children: [
      {
        path: 'view',
        loadComponent: () => import('./view/view').then((c) => c.FiledCasesView),
      },
      {
        path: 'details',
        loadComponent: () => import('./details/details').then((c) => c.FiledCaseDetails),
        title: 'Filed Case Details | CMS',
      },
      {
        path: 'details/:id',
        loadComponent: () => import('./details/details').then((c) => c.FiledCaseDetails),
        title: 'Filed Case Details | CMS',
      },
    ],
  },
];
