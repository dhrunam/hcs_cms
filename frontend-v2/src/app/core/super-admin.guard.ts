import { isPlatformBrowser } from '@angular/common';
import { inject, PLATFORM_ID } from '@angular/core';
import { CanMatchFn, Router } from '@angular/router';
import { AuthService } from '../auth.service';

/** Allows route only if the user belongs to the SUPERADMIN Django group. */
export const superAdminGuard: CanMatchFn = async () => {
  const platformId = inject(PLATFORM_ID);
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!isPlatformBrowser(platformId)) {
    return true;
  }

  try {
    await auth.initializeAuth();
    const groups = auth.getUserGroups().map((g) => String(g).toUpperCase());
    if (groups.includes('SUPERADMIN')) {
      return true;
    }
    return router.createUrlTree(['/superadmin/dashboard/home']);
  } catch {
    return router.createUrlTree(['/user/login']);
  }
};
