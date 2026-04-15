import { isPlatformBrowser } from '@angular/common';
import { HttpInterceptorFn } from '@angular/common/http';
import { inject, PLATFORM_ID } from '@angular/core';

/** Paths that must not send Bearer (token pair / refresh use body-only credentials). */
function isAnonymousTokenEndpoint(requestUrl: string): boolean {
  const u = requestUrl.toLowerCase();
  if (!u.includes('/accounts/auth/token/')) {
    return false;
  }
  if (u.includes('/accounts/auth/token/blacklist')) {
    return false;
  }
  if (u.includes('/accounts/auth/token/refresh')) {
    return true;
  }
  // Obtain pair: .../auth/token/ or .../auth/token
  return /\/accounts\/auth\/token\/?(\?|$)/.test(u);
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const platformId = inject(PLATFORM_ID);
  if (!isPlatformBrowser(platformId)) {
    return next(req);
  }
  if (isAnonymousTokenEndpoint(req.url)) {
    return next(req);
  }
  const token = sessionStorage.getItem('access_token')?.trim();
  if (!token) {
    return next(req);
  }
  return next(
    req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    }),
  );
};
