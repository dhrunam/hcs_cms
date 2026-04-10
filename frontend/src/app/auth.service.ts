import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { OAuthService } from 'angular-oauth2-oidc';
import { authConfig } from './auth.config';
import { app_url,  isLocalDevHost, sso_url } from './environment';
import { Router } from '@angular/router';
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
    private router: Router,
  ) {}

  async initAuth(): Promise<void> {
    // alert('initAuth');
    this.oauthService.configure(authConfig);
    try {
      // alert('loadDiscoveryDocumentAndTryLogin');
      await this.oauthService.loadDiscoveryDocumentAndTryLogin();
    } catch (error) {
      // alert('error in initAuth');
      // In local/dev flows SSO server may be offline; keep app usable.
      console.warn('SSO discovery unavailable, continuing without SSO session.');
    }
    this.syncSessionFromTokens();
    this.applyDevAuthBypassIfConfigured();
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

  /**
   * After SSO login, `user_group` is set from the token in {@link syncSessionFromTokens}.
   * Navigates to the dashboard for that role; falls back to group-based routing if unknown.
   */
  async navigateToDashboardByRole(): Promise<void> {
    let role = window.sessionStorage.getItem('user_group')?.trim() || null;
    if (!role) {
      const groups = this.getUserGroups();
      role = groups.find((g) => String(g).trim().length > 0)?.trim() ?? null;
    }

    let route = AuthService.dashboardRouteForRole(role);
    if (!route) {
      for (const g of this.getUserGroups()) {
        route = AuthService.dashboardRouteForRole(String(g).trim() || null);
        if (route) break;
      }
    }

    if (route) {
      await this.router.navigate(route);
      return;
    }
    await this.navigateToDashboardFromUserGroups();
  }

  /** Route commands for `router.navigate` — `null` means use {@link navigateToDashboardFromUserGroups}. */
  static dashboardRouteForRole(primaryRole: string | null): string[] | null {
    const r = primaryRole?.trim() || '';
    if (!r) return null;
    switch (r) {
      case 'API_ADVOCATE':
      case 'ADVOCATE':
        return ['/advocate/dashboard/home'];
      case 'API_SCRUTINY_OFFICER':
      case 'SCRUTINY_OFFICER':
        return ['/scrutiny-officers/dashboard/home'];
      case 'API_COURT_READER':
      case 'READER':
      case 'READER_CJ':
      case 'READER_J1':
      case 'READER_J2':
        return ['/reader/dashboard'];
      case 'API_LISTING_OFFICER':
      case 'LISTING_OFFICER':
        return ['/listing-officers/dashboard/home'];
      case 'API_JUDGE':
      case 'JUDGE_CJ':
      case 'JUDGE_J1':
      case 'JUDGE_J2':
        return ['/judges/dashboard/home'];
      case 'API_STENOGRAPHER':
        return ['/steno/dashboard/home'];
      default:
        return null;
    }
  }

  private async navigateToDashboardFromUserGroups(): Promise<void> {
    const groups = this.getUserGroups();

    if (groups.some((group) => ['JUDGE_CJ', 'JUDGE_J1', 'JUDGE_J2'].includes(group))) {
      await this.router.navigate(['/judges/dashboard/home']);
      return;
    }

    if (
      groups.some((group) =>
        ['READER', 'READER_CJ', 'READER_J1', 'READER_J2'].includes(group),
      )
    ) {
      await this.router.navigate(['/reader/dashboard']);
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

  /**
   * When `devAuthBypassToken` is set (localhost only), act as logged-in so the guard passes
   * and the interceptor sends the same Bearer token the backend dev auth accepts.
   */
  private applyDevAuthBypassIfConfigured(): void {
    // if (!isLocalDevHost() || !devAuthBypassToken?.trim()) {
    //   return;
    // }
    // if (this.oauthService.hasValidAccessToken()) {
    //   return;
    // }
    // const trimmed = devAuthBypassToken.trim();
    // sessionStorage.setItem('access_token', trimmed);
    // if (!sessionStorage.getItem('user_group')) {
    //   sessionStorage.setItem('user_group', 'ADVOCATE');
    //   sessionStorage.setItem('user_groups', JSON.stringify(['ADVOCATE']));
    // }
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
