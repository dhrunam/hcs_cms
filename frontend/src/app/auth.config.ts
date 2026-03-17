import { AuthConfig, OAuthService } from 'angular-oauth2-oidc';

export const authConfig: AuthConfig = {
  issuer: 'http://localhost:8000/o',
  // redirectUri: window.location.origin,
  redirectUri: 'http://localhost:4200/auth/redirect/',
  clientId: '5kWtcsPK1TeThWvN7gktrTfOsoiVdaY9OMqXEIV0',
  responseType: 'code',
  // scope: 'openid profile email read write api.read api.write offline_access',
  scope: 'openid profile email',
  showDebugInformation: false,
  strictDiscoveryDocumentValidation: false,
  requireHttps: false, // set true in production
  oidc: true,
  silentRefreshRedirectUri: window.location.origin + '/silent-refresh.html',
  useSilentRefresh: true,
  disablePKCE: false,
};
