import { AuthConfig, OAuthService } from 'angular-oauth2-oidc';

export const authConfig: AuthConfig = {
  issuer: "http://localhost:8000/o",
  // redirectUri: window.location.origin,
  redirectUri: "http://localhost:4200/",
  clientId: "4T0KMegeS4cY55z21J4pKP9RCHyuX5KpNUWDdiP7",
  responseType: "code",
  scope: "openid profile email",
  showDebugInformation: false,
  strictDiscoveryDocumentValidation: false,
  requireHttps: false, // set true in production
  oidc: true,
  silentRefreshRedirectUri: window.location.origin + "/silent-refresh.html",
  useSilentRefresh: true,
  disablePKCE: false,
};
