import { Routes } from '@angular/router';

export const DocumentFilingRoutes: Routes = [
  { path: '', redirectTo: 'view', pathMatch: 'full' },
  {
    path: '',
    loadComponent: () => import('./document-filing').then((c) => c.DocumentFiling),
    children: [
      { path: 'view', loadComponent: () => import('./view/view').then((c) => c.View) },
      { path: 'create', loadComponent: () => import('./create/create').then((c) => c.Create) },
      { path: 'edit/:id', loadComponent: () => import('./edit/edit').then((c) => c.Edit) },
    ],
  },
];

