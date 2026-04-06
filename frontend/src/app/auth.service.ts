import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { OAuthService } from 'angular-oauth2-oidc';
import { authConfig } from './auth.config';
import { app_url, sso_url } from './environment';

export type LogoutStatus = {
  apiSessionLoggedOut: boolean;
  ssoSessionLoggedOut: boolean;
  tokensCleared: boolean;
  success: boolean;
};

export type AuthorizationError = {
  error: string;
  errorDescription: string;
};

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly logoutUrl = `${app_url}/api/v1/accounts/users/logout/`;
  private readonly ssoLogoutUrl = `${sso_url}/accounts/logout/`;

  constructor(
    private oauthService: OAuthService,
    private http: HttpClient,
  ) {}

  async initAuth(): Promise<void> {
    this.oauthService.configure(authConfig);
    try {
      await this.oauthService.loadDiscoveryDocumentAndTryLogin();
    } catch (error) {
      // In local/dev flows SSO server may be offline; keep app usable.
      console.warn('SSO discovery unavailable, continuing without SSO session.');
    }
    this.syncSessionFromTokens();
  }

  login() {
    this.oauthService.initCodeFlow();
  }

  async logout(): Promise<LogoutStatus> {
    const csrfToken = this.getCookieValue('csrftoken');
    let apiSessionLoggedOut = false;
    let ssoSessionLoggedOut = false;

    try {
      await this.http
        .post(this.logoutUrl, {}, { withCredentials: true })
        .toPromise();
      apiSessionLoggedOut = true;
    } catch (error) {
      console.warn('Backend session logout failed (continuing with OAuth logout):', error);
    }

    try {
      await this.http
        .post(
          this.ssoLogoutUrl,
          {},
          {
            withCredentials: true,
            headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
          },
        )
        .toPromise();
      ssoSessionLoggedOut = true;
    } catch (error) {
      console.warn('SSO session logout failed:', error);
    }

    // Expire csrftoken from JS where possible; sessionid is HttpOnly and must be
    // invalidated by server-side logout endpoints.
    document.cookie = 'csrftoken=; Max-Age=0; path=/; SameSite=Lax';
    this.oauthService.logOut();
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('user_groups');
    sessionStorage.removeItem('user_group');

    const tokensCleared = !this.isLoggedIn();
    return {
      apiSessionLoggedOut,
      ssoSessionLoggedOut,
      tokensCleared,
      success: apiSessionLoggedOut && ssoSessionLoggedOut && tokensCleared,
    };
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

  public getAuthorizationError(): AuthorizationError | null {
    const params = new URLSearchParams(window.location.search);
    const error = params.get('error');

    if (!error) {
      return null;
    }

    return {
      error,
      errorDescription: params.get('error_description') || 'SSO login could not be completed.',
    };
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

  private getCookieValue(name: string): string {
    const cookies = document.cookie ? document.cookie.split(';') : [];

    for (const cookie of cookies) {
      const [rawKey, ...rawValue] = cookie.trim().split('=');
      if (rawKey === name) {
        return decodeURIComponent(rawValue.join('='));
      }
    }

    return '';
  }
}
