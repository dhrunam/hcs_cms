import { Routes } from "@angular/router";

export const EfilingRoutes: Routes = [
    {
        path: 'new-filing',
        loadComponent: () =>
            import('./new-filing/new-filing').then(c => c.NewFiling),
    },
    {
        path: 'draft-filings',
        loadComponent: () =>
            import('./draft-filings/draft-filings').then(c => c.DraftFilings),
    },
    {
        path: 'pending-cases',
        loadComponent: () =>
            import('./pending-cases/pending-cases').then(c => c.PendingCases),
    },
];