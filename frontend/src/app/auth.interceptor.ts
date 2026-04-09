import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { OAuthService } from 'angular-oauth2-oidc';
import { catchError, throwError } from 'rxjs';
import { devAuthBypassToken, isLocalDevHost } from './environment';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const oauthService = inject(OAuthService);
  const fromSession = sessionStorage.getItem('access_token');
  const fromLocal = localStorage.getItem('access_token');
  const fromOAuth = oauthService.getAccessToken() || '';
  let token = fromSession || fromLocal || fromOAuth || null;
  if (!token?.trim() && devAuthBypassToken?.trim() && isLocalDevHost()) {
    token = devAuthBypassToken.trim();
  }
  if (token && !fromSession) {
    sessionStorage.setItem('access_token', token);
  }

  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        sessionStorage.removeItem('access_token');
        router.navigate(['/error'], { queryParams: { code: 401 } });
      }
      if (error.status === 403) {
        router.navigate(['/error'], { queryParams: { code: 403 } });
      }
      if (error.status === 500) {
        router.navigate(['/error'], { queryParams: { code: 500 } });
      }
      return throwError(() => error);
    }),
  );
};
