import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  { path: 'user/login', renderMode: RenderMode.Client },
  { path: 'user/register', renderMode: RenderMode.Client },
  { path: 'user/register/advocate', renderMode: RenderMode.Client },
  { path: 'user/register/party', renderMode: RenderMode.Client },
  { path: 'user/verify-email', renderMode: RenderMode.Client },
  { path: 'superadmin/**', renderMode: RenderMode.Client },
  { path: 'admin/**', renderMode: RenderMode.Client },
  { path: 'advocate/**', renderMode: RenderMode.Client },
  { path: 'party/**', renderMode: RenderMode.Client },
  { path: 'judges/**', renderMode: RenderMode.Client },
  { path: 'reader/**', renderMode: RenderMode.Client },
  { path: 'listing-officers/**', renderMode: RenderMode.Client },
  { path: 'scrutiny-officers/**', renderMode: RenderMode.Client },
  { path: 'steno/**', renderMode: RenderMode.Client },
  {
    path: '**',
    renderMode: RenderMode.Prerender,
  },
];
