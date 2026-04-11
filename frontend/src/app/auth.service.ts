import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { app_url, devAuthBypassToken, isLocalDevHost, sessionProfileKey } from './environment';
import { Router } from '@angular/router';
import {
  USER_SESSION_ENC_KEY,
  UserSessionProfile,
  encryptUserSessionProfile,
} from './session-profile-crypto';

export type { UserSessionProfile } from './session-profile-crypto';

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
  /** Fallback when JWT payload cannot expose `groups` to the client (decode issues) or claims are empty. */
  private readonly userMeUrl = `${app_url}/api/v1/accounts/users/me/`;

  /** In-memory copy of `/users/me/` profile; mirrored encrypted in sessionStorage when configured. */
  private sessionProfileCache: UserSessionProfile | null = null;

  constructor(
    private http: HttpClient,
    private router: Router,
  ) {}

  async initAuth(): Promise<void> {
    this.applyDevAuthBypassIfConfigured();
    this.syncSessionFromJwtAccessToken();
    await this.syncEncryptedUserProfile();
  }

  /** Navigate to local login. */
  login(): void {
    void this.router.navigate(['/user/login']);
  }

  /**
   * JWT login against the CMS API; stores access/refresh in sessionStorage.
   * @param identifier Registered email or phone number (`User.phone_number`); sent as JSON `email`.
   */
  async loginWithPassword(identifier: string, password: string): Promise<void> {
    const res = await firstValueFrom(
      this.http.post<{ access: string; refresh: string }>(this.tokenUrl, {
        email: identifier.trim(),
        password,
      }),
    );
    if (res?.access) {
      sessionStorage.setItem('access_token', res.access);
      if (res.refresh) {
        sessionStorage.setItem('refresh_token', res.refresh);
      }
      this.syncSessionFromJwtAccessToken();
      await this.syncEncryptedUserProfile();
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

    // Session logout must run while access_token is still in sessionStorage so the
    // auth interceptor sends Authorization: Bearer (UserViewSet.logout is IsAuthenticated).
    let apiSessionLoggedOut = false;
    try {
      await firstValueFrom(this.http.post(this.logoutUrl, {}, { withCredentials: true }));
      apiSessionLoggedOut = true;
    } catch (error) {
      console.warn('Backend session logout failed:', error);
    }

    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user_groups');
    sessionStorage.removeItem('user_group');
    sessionStorage.removeItem(USER_SESSION_ENC_KEY);
    this.sessionProfileCache = null;
    document.cookie = 'csrftoken=; Max-Age=0; path=/; SameSite=Lax';

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

  /**
   * Django group names for routing and APIs; prefers decrypted/in-memory profile from `/users/me/`.
   */
  public getUserGroups(): string[] {
    if (this.sessionProfileCache?.groups && Array.isArray(this.sessionProfileCache.groups)) {
      return [...this.sessionProfileCache.groups];
    }
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

  /** Decrypted user profile (name, groups, email) after login or `initAuth`; null if not loaded yet. */
  public getSessionProfile(): UserSessionProfile | null {
    return this.sessionProfileCache;
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

  /**
   * Maps JWT `role` (lowercase key from API) and Django `Group.name` values
   * (e.g. JUDGE_CJ, READER_J1) to dashboard routes.
   */
  static dashboardRouteForRole(primaryRole: string | null): string[] | null {
    const r = primaryRole?.trim() || '';
    if (!r) return null;
    const u = r.toUpperCase();

    if (u === 'ADVOCATE' || r === 'advocate') {
      return ['/advocate/dashboard/home'];
    }
    if (u === 'PARTY_IN_PERSON' || r === 'party_in_person') {
      return ['/advocate/dashboard/home'];
    }
    if (u === 'SCRUTINY_OFFICER' || r === 'scrutiny_officer') {
      return ['/scrutiny-officers/dashboard/home'];
    }
    if (
      u === 'READER' ||
      r === 'reader' ||
      u.startsWith('READER_')
    ) {
      return ['/reader/dashboard'];
    }
    if (u === 'LISTING_OFFICER' || r === 'listing_officer') {
      return ['/listing-officers/dashboard/home'];
    }
    if (u === 'JUDGE' || r === 'judge' || u.startsWith('JUDGE_')) {
      return ['/judges/dashboard/home'];
    }
    if (u === 'STENO' || r === 'steno') {
      return ['/steno/dashboard/home'];
    }
    if (u === 'SUPERADMIN' || r === 'superadmin') {
      return ['/advocate/dashboard/home'];
    }
    return null;
  }

  private async navigateToDashboardFromUserGroups(): Promise<void> {
    const groups = this.getUserGroups();
    const has = (pred: (g: string) => boolean) => groups.some(pred);

    if (has((g) => g === 'JUDGE' || g.startsWith('JUDGE_'))) {
      await this.router.navigate(['/judges/dashboard/home']);
      return;
    }

    if (has((g) => g === 'READER' || g.startsWith('READER_'))) {
      await this.router.navigate(['/reader/dashboard']);
      return;
    }

    if (has((g) => g === 'LISTING_OFFICER')) {
      await this.router.navigate(['/listing-officers/dashboard/home']);
      return;
    }

    if (has((g) => g === 'SCRUTINY_OFFICER')) {
      await this.router.navigate(['/scrutiny-officers/dashboard/home']);
      return;
    }

    if (has((g) => g === 'STENO')) {
      await this.router.navigate(['/steno/dashboard/home']);
      return;
    }

    if (has((g) => g === 'PARTY_IN_PERSON')) {
      await this.router.navigate(['/advocate/dashboard/home']);
      return;
    }

    if (has((g) => g === 'ADVOCATE')) {
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
    this.sessionProfileCache = {
      displayName: 'Dev user',
      groups: ['ADVOCATE'],
    };
  }

  /** When JWT omits `groups`, derive a canonical group from `role` for routing. */
  private static primaryGroupForRoleKey(role: string): string | null {
    const m: Record<string, string> = {
      advocate: 'ADVOCATE',
      party_in_person: 'PARTY_IN_PERSON',
      scrutiny_officer: 'SCRUTINY_OFFICER',
      reader: 'READER',
      listing_officer: 'LISTING_OFFICER',
      steno: 'STENO',
      judge: 'JUDGE',
      superadmin: 'SUPERADMIN',
    };
    return m[role] ?? null;
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
    const role = typeof claims['role'] === 'string' ? claims['role'].trim() : '';
    let groups = AuthService.groupsFromClaims(claims);

    if (groups.length === 0 && role) {
      const fallback = AuthService.primaryGroupForRoleKey(role);
      if (fallback) {
        groups = [fallback];
      }
    }

    sessionStorage.setItem('user_groups', JSON.stringify(groups));
    if (role) {
      sessionStorage.setItem('user_group', role);
    } else if (groups.length > 0) {
      sessionStorage.setItem('user_group', groups[0]);
    } else {
      sessionStorage.removeItem('user_group');
    }
  }

  /** Normalize `groups` from JWT payload (array, JSON string, or missing). */
  private static groupsFromClaims(claims: Record<string, unknown>): string[] {
    const raw = claims['groups'];
    if (Array.isArray(raw)) {
      return raw.filter((g): g is string => typeof g === 'string' && g.length > 0);
    }
    if (typeof raw === 'string') {
      const s = raw.trim();
      if (!s) {
        return [];
      }
      try {
        const parsed: unknown = JSON.parse(s);
        if (Array.isArray(parsed)) {
          return parsed.filter((g): g is string => typeof g === 'string' && g.length > 0);
        }
      } catch {
        /* single group name */
      }
      return [s];
    }
    return [];
  }

  /**
   * Loads `/users/me/`, updates plain `user_groups` / `user_group` for routing, caches profile,
   * and stores an AES-GCM encrypted blob when `sessionProfileKey` is set.
   */
  private async syncEncryptedUserProfile(): Promise<void> {
    if (!this.isLoggedIn()) {
      return;
    }
    try {
      const me = await firstValueFrom(
        this.http.get<{
          full_name?: string;
          first_name?: string;
          last_name?: string;
          email?: string;
          groups?: string[];
          registration_type?: string;
        }>(this.userMeUrl),
      );
      const groups = Array.isArray(me?.groups)
        ? me.groups.filter((g) => typeof g === 'string' && g.trim().length > 0)
        : [];
      const displayName =
        (typeof me.full_name === 'string' && me.full_name.trim()) ||
        [me.first_name, me.last_name]
          .filter((x): x is string => typeof x === 'string' && !!x.trim())
          .join(' ')
          .trim() ||
        (typeof me.email === 'string' ? me.email : '');
      const profile: UserSessionProfile = {
        displayName,
        groups,
        email: typeof me.email === 'string' ? me.email : undefined,
        registration_type:
          typeof me.registration_type === 'string' ? me.registration_type : undefined,
      };
      this.sessionProfileCache = profile;
      sessionStorage.setItem('user_groups', JSON.stringify(groups));
      if (groups.length > 0) {
        sessionStorage.setItem('user_group', groups[0]);
      } else {
        sessionStorage.removeItem('user_group');
      }
      const enc = await encryptUserSessionProfile(profile, sessionProfileKey);
      if (enc) {
        sessionStorage.setItem(USER_SESSION_ENC_KEY, enc);
      } else {
        sessionStorage.removeItem(USER_SESSION_ENC_KEY);
      }
    } catch {
      /* 401 / network — leave existing cache and plain keys */
    }
  }

  /** UTF-8 safe JWT payload decode (atob alone breaks on non-ASCII in claims). */
  private decodeJwtPayload(accessToken: string): Record<string, unknown> | null {
    const tokenParts = accessToken.split('.');
    if (tokenParts.length < 2) {
      return null;
    }
    try {
      const base64 = tokenParts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, '=');
      const binary = atob(padded);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }
      const json = new TextDecoder('utf-8').decode(bytes);
      return JSON.parse(json) as Record<string, unknown>;
    } catch {
      return null;
    }
  }
}
