import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  // Get OAuth2 access_token from sessionStorage
  const token = sessionStorage.getItem('access_token');

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
      if (error.status === 400) {
        router.navigate(['/error'], { queryParams: { code: 400 } });
      }
      if (error.status === 500) {
        router.navigate(['/error'], { queryParams: { code: 500 } });
      }
      return throwError(() => error);
    }),
  );
};
