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

      await this.navigateToDashboard();
    } catch (err) {
      console.error('Auth initialization failed', err);
      await this.router.navigate(['/user/login']);
    }
  }

  private async navigateToDashboard(): Promise<void> {
    const groups = this.authService.getUserGroups();

    if (groups.some((group) => ['JUDGE_CJ', 'JUDGE_J1', 'JUDGE_J2'].includes(group))) {
      await this.router.navigate(['/judges/dashboard/home']);
      return;
    }

    if (groups.some((group) => ['READER', 'READER_CJ', 'READER_J1', 'READER_J2'].includes(group))) {
      await this.router.navigate(['/reader/dashboard/registered-cases']);
      return;
    }

    if (groups.includes('LISTING_OFFICER')) {
      await this.router.navigate(['/listing-officers/dashboard/home']);
      return;
    }

    if (groups.includes('SCRUTINY_OFFICER')) {
      await this.router.navigate(['/scrutiny-officers/dashboard/home']);
      return;
    }

    await this.router.navigate(['/advocate/dashboard/home']);
  }
}
