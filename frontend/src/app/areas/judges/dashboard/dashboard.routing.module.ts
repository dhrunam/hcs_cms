import { Routes } from '@angular/router';

export const JudgeDashboardRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./dashboard').then((c) => c.JudgeDashboard),
    children: [
      {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full',
      },
      {
        path: 'home',
        loadComponent: () =>
          import('./home/home').then((c) => c.JudgePendingCasesPage),
        title: 'Judge Courtroom | CMS',
      },
      {
        path: 'courtroom/:id',
        loadComponent: () =>
          import('./courtroom/courtroom').then((c) => c.JudgeCourtroomPage),
        title: 'Courtroom | CMS',
      },
      {
        path: 'courtview',
        loadComponent: () =>
          import('./courtview/courtview').then((c) => c.JudgeCourtviewPage),
        title: 'Courtview | CMS',
      },
      {
        path: 'courtview/case/:id',
        loadComponent: () =>
          import('./courtview-case/courtview-case').then((c) => c.JudgeCourtviewCasePage),
        title: 'Courtview Case | CMS',
      },
      {
        path: 'steno-review',
        loadComponent: () =>
          import('./steno-review/steno-review').then((c) => c.JudgeStenoReviewPage),
        title: 'Judge | Steno Review',
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

