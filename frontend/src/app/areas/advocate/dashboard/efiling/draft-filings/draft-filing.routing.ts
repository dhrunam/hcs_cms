import { Routes } from '@angular/router';

export const DraftFilingRoutes: Routes = [
  { path: '', redirectTo: 'view', pathMatch: 'full' },
  {
    path: '',
    loadComponent: () => import('./draft-filings').then((c) => c.DraftFilings),
    children: [
      { path: 'view', loadComponent: () => import('./view/view').then((c) => c.View) },
      
    ],
  },
];
