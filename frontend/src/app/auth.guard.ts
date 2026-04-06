import { inject } from '@angular/core';
import { CanMatchFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanMatchFn = async () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  try {
    await authService.initializeAuth();

    if (authService.isLoggedIn()) {
      return true;
    }

    authService.login();
    return false;
  } catch (error) {
    console.error('Auth guard initialization failed', error);
    return router.parseUrl('/user/login');
  }
};