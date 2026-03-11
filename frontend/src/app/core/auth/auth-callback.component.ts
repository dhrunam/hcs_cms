import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { OAuthService } from 'angular-oauth2-oidc';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-auth-callback',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule],
  template: `
    <div class="callback-container">
      <mat-spinner diameter="48"></mat-spinner>
      <p>Completing sign-in&hellip;</p>
    </div>
  `,
  styles: [`
    .callback-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      gap: 16px;
    }
  `],
})
export class AuthCallbackComponent implements OnInit {
  constructor(
    private oauthService: OAuthService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    if (this.oauthService.hasValidAccessToken()) {
      this.router.navigate(['/cases']);
    } else {
      this.router.navigate(['/login']);
    }
  }
}
