import { Routes } from '@angular/router';

export const DocumentFilingRoutes: Routes = [
  { path: '', redirectTo: 'create', pathMatch: 'full' },
  {
    path: '',
    loadComponent: () => import('./document-filing').then((c) => c.DocumentFiling),
    children: [
      { path: 'create', loadComponent: () => import('./create/create').then((c) => c.Create) },
    ],
  },
];
