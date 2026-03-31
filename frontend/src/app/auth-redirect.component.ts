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
      await this.authService.initializeAuth();
      const groups = this.authService.getUserGroups();

      if (groups.some((g) => ['JUDGE_CJ', 'JUDGE_J1', 'JUDGE_J2'].includes(g))) {
        await this.router.navigate(['/judges/dashboard/home']);
      } else if (groups.includes('READER')) {
        await this.router.navigate(['/reader/pending-dates']);
      } else if (groups.includes('LISTING_OFFICER')) {
        await this.router.navigate(['/listing-officers/dashboard/home']);
      } else {
        await this.router.navigate(['/advocate/dashboard/home']);
      }
    } catch (err) {
      console.error('Auth initialization failed', err);
      await this.router.navigate(['/user/login']);
    }
  }
}
