import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { app_url, devAuthBypassToken, isLocalDevHost, sessionProfileKey } from './environment';
import { Router } from '@angular/router';
import {
  USER_SESSION_ENC_KEY,
  UserSessionProfile,
  decryptUserSessionProfile,
  encryptUserSessionProfile,
} from './session-profile-crypto';

export type { UserSessionProfile } from './session-profile-crypto';

export type LogoutStatus = {
  apiSessionLoggedOut: boolean;
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
  private readonly userMeUrl = `${app_url}/api/v1/accounts/users/me/`;

  private sessionProfileCache: UserSessionProfile | null = null;

  constructor(
    private http: HttpClient,
    private router: Router,
  ) {}

  async initAuth(): Promise<void> {
    this.applyDevAuthBypassIfConfigured();
    this.syncSessionFromJwtAccessToken();
    await this.hydrateSessionProfileFromEncryptedStorage();
    await this.syncEncryptedUserProfile();
  }

  login(): void {
    void this.router.navigate(['/user/login']);
  }

  async loginWithPassword(identifier: string, password: string): Promise<void> {
    const res = await firstValueFrom(
      this.http.post<{ access?: string; refresh?: string }>(this.tokenUrl, {
        email: identifier.trim(),
        password,
      }),
    );
    if (!res?.access) {
      throw new Error('Sign-in did not return an access token. Please try again.');
    }
    sessionStorage.setItem('access_token', res.access);
    if (res.refresh) {
      sessionStorage.setItem('refresh_token', res.refresh);
    }
    this.syncSessionFromJwtAccessToken();
    await this.hydrateSessionProfileFromEncryptedStorage();
    await this.syncEncryptedUserProfile();
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

  public getUserGroups(): string[] {
    if (this.sessionProfileCache?.groups && Array.isArray(this.sessionProfileCache.groups)) {
      return [...this.sessionProfileCache.groups];
    }
    const rawGroups =
      sessionStorage.getItem('user_groups') ?? localStorage.getItem('user_groups');
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

  public getSessionProfile(): UserSessionProfile | null {
    return this.sessionProfileCache;
  }

  /**
   * Full display string for names and initials (not truncated).
   */
  public getUserDisplayNameRaw(): string {
    const p = this.sessionProfileCache;
    const fromProfile =
      p?.displayName?.trim() || p?.email?.trim() || p?.username?.trim() || '';
    if (fromProfile) {
      return fromProfile;
    }
    const token = sessionStorage.getItem('access_token');
    if (token) {
      const claims = this.decodeJwtPayload(token);
      if (claims) {
        const fromJwt = AuthService.displayNameFromJwtClaims(claims);
        if (fromJwt) {
          return fromJwt;
        }
      }
    }
    return 'User';
  }

  /**
   * Name shown in the shell header (truncated). Uses profile, then email / username, then JWT claims.
   */
  public getUserDisplayLabel(): string {
    const raw = this.getUserDisplayNameRaw();
    return raw.length > 28 ? raw.slice(0, 26) + '…' : raw;
  }

  /**
   * Human-readable role(s) from `/users/me` groups (session profile), then `sessionStorage`
   * (`user_groups`, `user_group`), then JWT `role` claim.
   */
  public getUserRoleDisplayLabel(): string {
    const groups = this.getUserGroups().filter((g) => String(g).trim().length > 0);
    if (groups.length > 0) {
      return groups.map((g) => AuthService.formatRoleGroupName(String(g))).join(', ');
    }
    const single =
      sessionStorage.getItem('user_group')?.trim() ?? localStorage.getItem('user_group')?.trim();
    if (single) {
      return AuthService.formatRoleGroupName(single);
    }
    const token = sessionStorage.getItem('access_token');
    if (token) {
      const claims = this.decodeJwtPayload(token);
      const role = typeof claims?.['role'] === 'string' ? claims['role'].trim() : '';
      if (role) {
        return AuthService.formatRoleGroupName(role);
      }
    }
    return '—';
  }

  /** Maps Django group names / JWT role keys to display labels. */
  private static formatRoleGroupName(raw: string): string {
    const n = raw.trim();
    if (!n) {
      return '';
    }
    const upper = n.toUpperCase();
    const groupLabels: Record<string, string> = {
      ADVOCATE: 'Advocate',
      PARTY_IN_PERSON: 'Party in person',
      SCRUTINY_OFFICER: 'Scrutiny officer',
      READER: 'Reader',
      LISTING_OFFICER: 'Listing officer',
      STENO: 'Steno',
      JUDGE: 'Judge',
      SUPERADMIN: 'Super admin',
    };
    if (groupLabels[upper]) {
      return groupLabels[upper];
    }
    const norm = n.toLowerCase().replace(/\s+/g, '_');
    const roleKeyLabels: Record<string, string> = {
      superadmin: 'Super admin',
      advocate: 'Advocate',
      party_in_person: 'Party in person',
      scrutiny_officer: 'Scrutiny officer',
      reader: 'Reader',
      listing_officer: 'Listing officer',
      steno: 'Steno',
      judge: 'Judge',
    };
    if (roleKeyLabels[norm]) {
      return roleKeyLabels[norm];
    }
    if (upper.startsWith('JUDGE_')) {
      const rest = n.slice(6).replace(/_/g, ' ').trim();
      return rest ? `Judge · ${rest}` : 'Judge';
    }
    if (upper.startsWith('READER_')) {
      const rest = n.slice(7).replace(/_/g, ' ').trim();
      return rest ? `Reader · ${rest}` : 'Reader';
    }
    return n
      .replace(/_/g, ' ')
      .replace(/\w\S*/g, (w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase());
  }

  private static displayNameFromJwtClaims(claims: Record<string, unknown>): string {
    const str = (k: string): string | undefined =>
      typeof claims[k] === 'string' ? (claims[k] as string).trim() || undefined : undefined;
    return (
      str('name') ||
      [str('given_name'), str('family_name')].filter(Boolean).join(' ').trim() ||
      str('preferred_username') ||
      str('email') ||
      str('username') ||
      ''
    );
  }

  private async hydrateSessionProfileFromEncryptedStorage(): Promise<void> {
    const p = this.sessionProfileCache;
    if (p?.displayName?.trim() || p?.email?.trim() || p?.username?.trim()) {
      return;
    }
    const stored = sessionStorage.getItem(USER_SESSION_ENC_KEY);
    if (!stored || !sessionProfileKey?.trim()) {
      return;
    }
    const profile = await decryptUserSessionProfile(stored, sessionProfileKey);
    if (!profile) {
      return;
    }
    this.sessionProfileCache = profile;
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
    const u = r.toUpperCase();

    if (u === 'SUPERADMIN' || r === 'superadmin') {
      return ['/superadmin/dashboard/home'];
    }
    if (u === 'ADVOCATE' || r === 'advocate') {
      return ['/advocate/dashboard/home'];
    }
    if (u === 'PARTY_IN_PERSON' || r === 'party_in_person') {
      return ['/party/dashboard/home'];
    }
    if (u === 'SCRUTINY_OFFICER' || r === 'scrutiny_officer') {
      return ['/scrutiny-officers/dashboard/home'];
    }
    if (u === 'READER' || r === 'reader' || u.startsWith('READER_')) {
      return ['/reader/dashboard/home'];
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
    return null;
  }

  private async navigateToDashboardFromUserGroups(): Promise<void> {
    const groups = this.getUserGroups();
    const has = (pred: (g: string) => boolean) => groups.some(pred);

    if (has((g) => g === 'SUPERADMIN')) {
      await this.router.navigate(['/superadmin/dashboard/home']);
      return;
    }

    if (has((g) => g === 'JUDGE' || g.startsWith('JUDGE_'))) {
      await this.router.navigate(['/judges/dashboard/home']);
      return;
    }

    if (has((g) => g === 'READER' || g.startsWith('READER_'))) {
      await this.router.navigate(['/reader/dashboard/home']);
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
      await this.router.navigate(['/party/dashboard/home']);
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
          username?: string;
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
        (typeof me.email === 'string' ? me.email.trim() : '') ||
        (typeof me.username === 'string' ? me.username.trim() : '') ||
        '';
      const profile: UserSessionProfile = {
        displayName,
        groups,
        email: typeof me.email === 'string' ? me.email : undefined,
        username: typeof me.username === 'string' ? me.username : undefined,
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
