import { Routes } from '@angular/router';

export const IaFilingRoutes: Routes = [
  { path: '', redirectTo: 'view', pathMatch: 'full' },
  {
    path: '',
    loadComponent: () => import('./ia-filing').then((c) => c.IaFiling),
    children: [
      { path: 'view', loadComponent: () => import('./view/view').then((c) => c.IaFilingView) },
      { path: 'create', loadComponent: () => import('./filing-form/filing-form').then((c) => c.IaFilingForm) },
      { path: 'edit/:id', loadComponent: () => import('./edit/edit').then((c) => c.IaFilingEdit) },
    ],
  },
];
