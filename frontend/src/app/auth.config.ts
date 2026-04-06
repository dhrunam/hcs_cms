import { AuthConfig, OAuthService } from 'angular-oauth2-oidc';

export const authConfig: AuthConfig = {
  issuer: 'http://localhost:8000/o',
  // redirectUri: window.location.origin,
  redirectUri: 'http://localhost:4200/',
  clientId: 'VEd9ZSHfK3m99blkADk5mkeUT99Ly0rpfaiJT987',
  responseType: 'code',
  scope: 'openid profile email',
  showDebugInformation: false,
  strictDiscoveryDocumentValidation: false,
  requireHttps: false, // set true in production
  oidc: true,
  silentRefreshRedirectUri: window.location.origin + '/silent-refresh.html',
  useSilentRefresh: true,
  disablePKCE: false,
};
