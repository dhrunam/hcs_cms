import { Injectable } from '@angular/core';
import { OAuthService, AuthConfig } from 'angular-oauth2-oidc';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(private oauthService: OAuthService) {}

  configureOAuth(): Promise<boolean> {
    const authConfig: AuthConfig = {
      issuer: environment.ssoConfig.issuer,
      redirectUri: environment.ssoConfig.redirectUri,
      clientId: environment.ssoConfig.clientId,
      responseType: environment.ssoConfig.responseType,
      scope: environment.ssoConfig.scope,
      useSilentRefresh: environment.ssoConfig.useSilentRefresh,
      showDebugInformation: environment.ssoConfig.showDebugInformation,
      requireHttps: environment.ssoConfig.requireHttps,
      pkce: environment.ssoConfig.pkce,
      clearHashAfterLogin: environment.ssoConfig.clearHashAfterLogin,
      tokenEndpoint: environment.ssoConfig.tokenEndpoint,
      userinfoEndpoint: environment.ssoConfig.userinfoEndpoint,
      logoutUrl: environment.ssoConfig.logoutUrl,
      oidc: environment.ssoConfig.oidc,
      strictDiscoveryDocumentValidation: false,
    };

    this.oauthService.configure(authConfig);
    this.oauthService.setupAutomaticSilentRefresh();

    return this.oauthService.loadDiscoveryDocumentAndTryLogin();
  }

  login(): void {
    this.oauthService.initCodeFlow();
  }

  logout(): void {
    try {
      this.oauthService.revokeTokenAndLogout();
    } catch {
      this.oauthService.logOut();
    }
  }

  isAuthenticated(): boolean {
    return this.oauthService.hasValidAccessToken();
  }

  getAccessToken(): string {
    return this.oauthService.getAccessToken();
  }

  getUserInfo(): Record<string, unknown> {
    return (this.oauthService.getIdentityClaims() as Record<string, unknown>) ?? {};
  }

  getUserName(): string {
    const claims = this.getUserInfo();
    if (!claims) return '';
    return (
      (claims['name'] as string) ||
      (claims['email'] as string) ||
      (claims['preferred_username'] as string) ||
      ''
    );
  }
}
