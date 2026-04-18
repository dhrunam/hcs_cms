import { Routes } from '@angular/router';

export const ListingOfficerDashboardRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./dashboard').then((c) => c.ListingOfficerDashboard),
    children: [
      {
        path: '',
        redirectTo: 'generate-cause-list',
        pathMatch: 'full',
      },
      {
        path: 'home',
        redirectTo: 'generate-cause-list',
        pathMatch: 'full',
      },
      {
        path: 'listed-cases',
        loadComponent: () =>
          import('./listed-cases/listed-cases').then((c) => c.ListedCasesPage),
        title: 'Listed Cases | CMS',
      },
      {
        path: 'case/:id',
        loadComponent: () =>
          import('./case-summary/case-summary').then((c) => c.ListingCaseSummaryPage),
        title: 'Case Summary | CMS',
      },
      {
        path: 'generate-cause-list',
        loadComponent: () => import('./home/home').then((c) => c.ListingOfficerHome),
        title: 'Cause List Generator | CMS',
      },
      {
        path: 'office-note-sheet',
        loadComponent: () =>
          import('../../office-note-sheet/list/list').then((c) => c.OfficeNoteSheetList),
        title: 'Office Note Sheet | CMS',
      },
      {
        path: 'office-note-sheet/note/:caseId',
        loadComponent: () =>
          import('../../office-note-sheet/note-editor/note-editor').then((c) => c.OfficeNoteEditor),
        title: 'Case Notes | CMS',
      },
    ],
  },
];

