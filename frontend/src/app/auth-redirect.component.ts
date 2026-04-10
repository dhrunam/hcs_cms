import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-auth-redirect',
  template: '<p class="p-3">Signing you in...</p>',
})
export class AuthRedirectComponent implements OnInit {
  constructor(
    private authService: AuthService,
    private router: Router,
  ) {}

  async ngOnInit(): Promise<void> {

    // alert('AuthRedirectComponent');
    try {
      const authError = this.authService.getAuthorizationError();
      if (authError) {
        await this.router.navigate(['/user/login'], {
          queryParams: {
            auth_error: authError.error,
            auth_error_description: authError.errorDescription,
          },
        });
        return;
      }

      await this.authService.initializeAuth();
      if (!this.authService.isLoggedIn()) {
        this.authService.login();
        return;
      }

      await this.authService.navigateToDashboardByRole();
    } catch (err) {
      console.error('Auth initialization failed', err);
      await this.router.navigate(['/user/login']);
    }
  }
}
