import { Routes } from '@angular/router';

export const DocumentFilingRoutes: Routes = [
  { path: '', redirectTo: 'list', pathMatch: 'full' },
  {
    path: '',
    loadComponent: () => import('./document-filing').then((c) => c.DocumentFiling),
    children: [
      { path: 'list', loadComponent: () => import('./view/view').then((c) => c.DocumentFilingView) },
      { path: 'create', loadComponent: () => import('./create/create').then((c) => c.Create) },
    ],
  },
];
