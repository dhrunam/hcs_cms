import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { OAuthService } from 'angular-oauth2-oidc';
import { authConfig } from './auth.config';
import { app_url } from './environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly logoutUrl = `${app_url}/api/v1/accounts/users/logout/`;

  constructor(
    private oauthService: OAuthService,
    private http: HttpClient,
  ) {}

  async initAuth(): Promise<void> {
    this.oauthService.configure(authConfig);
    await this.oauthService.loadDiscoveryDocumentAndTryLogin();
    this.syncSessionFromTokens();
  }

  login() {
    this.oauthService.initCodeFlow();
  }

  async logout(): Promise<void> {
    try {
      await this.http
        .post(this.logoutUrl, {}, { withCredentials: true })
        .toPromise();
    } catch (error) {
      console.warn('Backend session logout failed (continuing with OAuth logout):', error);
    } finally {
      // Expire the csrftoken cookie from JS (it is not HttpOnly so JS can touch it).
      // The sessionid (HttpOnly) is deleted server-side via delete_cookie.
      document.cookie = 'csrftoken=; Max-Age=0; path=/; SameSite=Lax';
      this.oauthService.logOut();
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('user_groups');
      sessionStorage.removeItem('user_group');
    }
  }

  get accessToken() {
    return this.oauthService.getAccessToken();
  }

  public initializeAuth(): Promise<void> {
    return this.initAuth();
  }

  public getUserGroups(): string[] {
    const rawGroups = sessionStorage.getItem('user_groups');
    if (!rawGroups) {
      return [];
    }

    try {
      const parsed = JSON.parse(rawGroups);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  public isLoggedIn(): boolean {
    return (
      this.oauthService.hasValidAccessToken() ||
      this.oauthService.hasValidIdToken() ||
      !!this.oauthService.getAccessToken() ||
      !!this.oauthService.getIdToken() ||
      !!sessionStorage.getItem('access_token') ||
      !!localStorage.getItem('access_token')
    );
  }

  private syncSessionFromTokens(): void {
    const accessToken = this.oauthService.getAccessToken();
    if (accessToken) {
      sessionStorage.setItem('access_token', accessToken);
    }

    const identityClaims = this.oauthService.getIdentityClaims() as Record<string, unknown> | null;
    const accessTokenClaims = this.getAccessTokenClaims();
    const groups = [
      ...this.extractGroups(identityClaims),
      ...this.extractGroups(accessTokenClaims),
    ];

    const uniqueGroups = Array.from(new Set(groups));
    if (uniqueGroups.length > 0) {
      sessionStorage.setItem('user_groups', JSON.stringify(uniqueGroups));
      sessionStorage.setItem('user_group', uniqueGroups[0]);
    }
  }

  private getAccessTokenClaims(): Record<string, unknown> | null {
    const accessToken = this.oauthService.getAccessToken();
    if (!accessToken) {
      return null;
    }

    const tokenParts = accessToken.split('.');
    if (tokenParts.length < 2) {
      return null;
    }

    try {
      const payload = tokenParts[1].replace(/-/g, '+').replace(/_/g, '/');
      const decoded = atob(payload.padEnd(Math.ceil(payload.length / 4) * 4, '='));
      return JSON.parse(decoded) as Record<string, unknown>;
    } catch {
      return null;
    }
  }

  private extractGroups(claims: Record<string, unknown> | null): string[] {
    if (!claims) {
      return [];
    }

    const groupCandidates: unknown[] = [
      claims['groups'],
      claims['group'],
      claims['roles'],
      (claims['realm_access'] as { roles?: unknown } | undefined)?.roles,
    ];

    const selected = groupCandidates.find((candidate) => candidate !== undefined && candidate !== null);

    if (Array.isArray(selected)) {
      return selected.filter((item): item is string => typeof item === 'string' && item.trim().length > 0);
    }

    if (typeof selected === 'string' && selected.trim().length > 0) {
      return [selected];
    }

    return [];
  }
}
