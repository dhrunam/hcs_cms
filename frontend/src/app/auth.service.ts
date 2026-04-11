import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { app_url, devAuthBypassToken, isLocalDevHost } from './environment';
import { Router } from '@angular/router';

export type LogoutStatus = {
  apiSessionLoggedOut: boolean;
  /** True when the refresh token was revoked on the server (JWT blacklist). */
  refreshBlacklisted: boolean;
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
  private readonly tokenUrl = `${app_url}/api/v1/accounts/auth/token/`;
  private readonly tokenBlacklistUrl = `${app_url}/api/v1/accounts/auth/token/blacklist/`;
  private readonly logoutUrl = `${app_url}/api/v1/accounts/users/logout/`;

  constructor(
    private http: HttpClient,
    private router: Router,
  ) {}

  async initAuth(): Promise<void> {
    this.syncSessionFromJwtAccessToken();
    this.applyDevAuthBypassIfConfigured();
  }

  /** Navigate to local login. */
  login(): void {
    void this.router.navigate(['/user/login']);
  }

  /** JWT login against the CMS API; stores access/refresh in sessionStorage. */
  async loginWithPassword(email: string, password: string): Promise<void> {
    const res = await firstValueFrom(
      this.http.post<{ access: string; refresh: string }>(this.tokenUrl, {
        email,
        password,
      }),
    );
    if (res?.access) {
      sessionStorage.setItem('access_token', res.access);
      if (res.refresh) {
        sessionStorage.setItem('refresh_token', res.refresh);
      }
      this.syncSessionFromJwtAccessToken();
    }
  }

  async logout(): Promise<LogoutStatus> {
    const refresh = sessionStorage.getItem('refresh_token');
    let refreshBlacklisted = false;
    if (refresh) {
      try {
        await firstValueFrom(this.http.post(this.tokenBlacklistUrl, { refresh }));
        refreshBlacklisted = true;
      } catch (error) {
        console.warn('Refresh token blacklist failed:', error);
      }
    }

    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user_groups');
    sessionStorage.removeItem('user_group');
    document.cookie = 'csrftoken=; Max-Age=0; path=/; SameSite=Lax';

    let apiSessionLoggedOut = false;
    try {
      await firstValueFrom(this.http.post(this.logoutUrl, {}, { withCredentials: true }));
      apiSessionLoggedOut = true;
    } catch (error) {
      console.warn('Backend session logout failed:', error);
    }

    const tokensCleared = !this.isLoggedIn();
    return {
      apiSessionLoggedOut,
      refreshBlacklisted,
      tokensCleared,
      success: tokensCleared,
    };
  }

  get accessToken(): string | null {
    return sessionStorage.getItem('access_token');
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

  static dashboardRouteForRole(primaryRole: string | null): string[] | null {
    const r = primaryRole?.trim() || '';
    if (!r) return null;
    switch (r) {
      case 'advocate':
      case 'API_ADVOCATE':
      case 'ADVOCATE':
        return ['/advocate/dashboard/home'];
      case 'party_in_person':
      case 'PARTY_IN_PERSON':
        return ['/advocate/dashboard/home'];
      case 'scrutiny_officer':
      case 'API_SCRUTINY_OFFICER':
      case 'SCRUTINY_OFFICER':
        return ['/scrutiny-officers/dashboard/home'];
      case 'reader':
      case 'API_COURT_READER':
      case 'READER':
      case 'READER_CJ':
      case 'READER_J1':
      case 'READER_J2':
        return ['/reader/dashboard'];
      case 'listing_officer':
      case 'API_LISTING_OFFICER':
      case 'LISTING_OFFICER':
        return ['/listing-officers/dashboard/home'];
      case 'judge':
      case 'API_JUDGE':
      case 'JUDGE_CJ':
      case 'JUDGE_J1':
      case 'JUDGE_J2':
      case 'JUDGE':
        return ['/judges/dashboard/home'];
      case 'steno':
      case 'API_STENOGRAPHER':
      case 'STENO':
        return ['/steno/dashboard/home'];
      default:
        return null;
    }
  }

  private async navigateToDashboardFromUserGroups(): Promise<void> {
    const groups = this.getUserGroups();

    if (groups.includes('JUDGE')) {
      await this.router.navigate(['/listing-officers/dashboard/home']);
      return;
    }

    if (groups.includes('READER')) {
      await this.router.navigate(['/listing-officers/dashboard/home']);
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

    if (groups.includes('STENO')) {
      await this.router.navigate(['/steno/dashboard/home']);
      return;
    }

    if (groups.includes('PARTY_IN_PERSON')) {
      await this.router.navigate(['/advocate/dashboard/home']);
      return;
    }

    if (groups.includes('ADVOCATE')) {
      await this.router.navigate(['/advocate/dashboard/home']);
      return;
    }

    await this.router.navigate(['/advocate/dashboard/home']);
  }

  public isLoggedIn(): boolean {
    return !!sessionStorage.getItem('access_token');
  }

  public getAuthorizationError(): AuthorizationError | null {
    const params = new URLSearchParams(window.location.search);
    const error = params.get('error');

    if (!error) {
      return null;
    }

    return {
      error,
      errorDescription: params.get('error_description') || 'Login could not be completed.',
    };
  }

  private applyDevAuthBypassIfConfigured(): void {
    if (!isLocalDevHost() || !devAuthBypassToken?.trim()) {
      return;
    }
    if (sessionStorage.getItem('access_token')) {
      return;
    }
    const trimmed = devAuthBypassToken.trim();
    sessionStorage.setItem('access_token', trimmed);
    if (!sessionStorage.getItem('user_group')) {
      sessionStorage.setItem('user_group', 'ADVOCATE');
      sessionStorage.setItem('user_groups', JSON.stringify(['ADVOCATE']));
    }
  }

  private syncSessionFromJwtAccessToken(): void {
    const accessToken = sessionStorage.getItem('access_token');
    if (!accessToken) {
      return;
    }
    const claims = this.decodeJwtPayload(accessToken);
    if (!claims) {
      return;
    }
    const role = typeof claims['role'] === 'string' ? claims['role'] : '';
    const groups = Array.isArray(claims['groups'])
      ? claims['groups'].filter((g): g is string => typeof g === 'string' && g.length > 0)
      : [];
    if (groups.length > 0) {
      sessionStorage.setItem('user_groups', JSON.stringify(groups));
    }
    if (role) {
      sessionStorage.setItem('user_group', role);
    } else if (groups.length > 0) {
      sessionStorage.setItem('user_group', groups[0]);
    }
  }

  private decodeJwtPayload(accessToken: string): Record<string, unknown> | null {
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
}
