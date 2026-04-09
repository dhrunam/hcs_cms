import { AuthConfig, OAuthService } from 'angular-oauth2-oidc';

export const authConfig: AuthConfig = {
  issuer: "http://localhost:8000/o",
  // redirectUri: window.location.origin,
  redirectUri: 'http://localhost:4200/',
  clientId: '3BaGLodbo7AdK5qjIjK1I0Isf1l5zLnGqiOC6Oov',
  responseType: 'code',
  scope: 'openid profile email',
  showDebugInformation: false,
  strictDiscoveryDocumentValidation: false,
  requireHttps: false, // set true in production
  oidc: true,
  silentRefreshRedirectUri: window.location.origin + "/silent-refresh.html",
  useSilentRefresh: true,
  disablePKCE: false,
};
