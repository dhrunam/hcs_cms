import { Injectable } from '@angular/core';
import { OAuthService } from 'angular-oauth2-oidc';
import { authConfig } from './auth.config';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private logoutUrl = 'http://localhost:8000/api/users/logout/';

  constructor(
    private oauthService: OAuthService,
    private http: HttpClient,
  ) {}

  async initAuth(): Promise<void> {
    this.oauthService.configure(authConfig);
    await this.oauthService.loadDiscoveryDocumentAndTryLogin();
  }

  login() {
    this.oauthService.logOut();

    this.oauthService.initCodeFlow();
  }

  async logout(): Promise<void> {
    try {
      // Call your custom logout endpoint
      await this.http.post(this.logoutUrl, {}, { withCredentials: true }).toPromise();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear OIDC tokens locally
      this.oauthService.logOut();
    }
  }

  get accessToken() {
    return this.oauthService.getAccessToken();
  }

  public initializeAuth(): Promise<void> {
    return this.initAuth();
  }

  public isLoggedIn(): boolean {
    // if using angular-oauth2-oidc
    return this.oauthService.hasValidAccessToken();
  }
}
