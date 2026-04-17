import { Routes } from '@angular/router';

export const OfficeNoteSheetRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./office-note-sheet').then((c) => c.OfficeNoteSheet),
    children: [
      {
        path: '',
        redirectTo: 'list',
        pathMatch: 'full',
      },
      {
        path: 'list',
        loadComponent: () => import('./list/list').then((c) => c.OfficeNoteSheetList),
        title: 'Office Note Sheet | CMS',
      },
      {
        path: 'note/:caseId',
        loadComponent: () => import('./note-editor/note-editor').then((c) => c.OfficeNoteEditor),
        title: 'Case Notes | CMS',
      },
    ],
  },
];