import { Routes } from "@angular/router";

export const EfilingRoutes: Routes = [
    { path: 'new-filing', loadComponent: () => import('./new-filing/new-filing').then(c => c.NewFiling ) },
]