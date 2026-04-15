import { isPlatformBrowser } from '@angular/common';
import { inject, PLATFORM_ID } from '@angular/core';
import { CanMatchFn, Router } from '@angular/router';
import { AuthService } from '../auth.service';

/** Requires a stored JWT; redirects unauthenticated users to `/user/login`. */
export const authGuard: CanMatchFn = async () => {
  const platformId = inject(PLATFORM_ID);
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!isPlatformBrowser(platformId)) {
    return true;
  }

  try {
    await authService.initializeAuth();
    if (authService.isLoggedIn()) {
      return true;
    }
    return router.createUrlTree(['/user/login']);
  } catch {
    return router.createUrlTree(['/user/login']);
  }
};
