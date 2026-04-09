//local url

export const url = 'http://localhost';

export const app_url = `${url}:8002`;
export const sso_url = `${url}:8000`;

/** True when the SPA runs on localhost (dev bypass is ignored elsewhere). */
export function isLocalDevHost(): boolean {
  if (typeof window === 'undefined') return false;
  const h = window.location.hostname;
  return h === 'localhost' || h === '127.0.0.1';
}

/**
 * Must match backend `DEV_AUTH_BYPASS_TOKEN` in `.env` (see `.env.example`).
 * Only used on localhost when no valid SSO access token is present.
 * Set to "" to disable and rely on SSO only.
 */
export const devAuthBypassToken = 'local-hcs-cms-dev-only';
