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
    } finally {
      await this.router.navigate(['/advocate/dashboard/home']);
    }
  }
}
