import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./advocate').then((m) => m.Advocate),
    children: [
      {
        path: '',
        loadComponent: () => import('./dashboard/dashboard').then((m) => m.Dashboard),
      },
    ],
  },
];
