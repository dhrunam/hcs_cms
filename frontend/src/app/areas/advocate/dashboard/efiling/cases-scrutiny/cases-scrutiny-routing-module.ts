import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./cases-scrutiny').then((c) => c.CasesScrutiny),
    children: [
      { path: '', loadComponent: () => import('./view/view').then((c) => c.View) },
      {
        path: 'details/:id',
        loadComponent: () =>
          import('./scrutiny-details/scrutiny-details').then((c) => c.ScrutinyDetails),
      },
    ],
  },
];
