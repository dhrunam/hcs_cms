//local url

export const url = 'http://localhost';

export const app_url = `${url}:8002`;

/** True when the SPA runs on localhost (dev bypass is ignored elsewhere). */
export function isLocalDevHost(): boolean {
  if (typeof window === 'undefined') return false;
  const h = window.location.hostname;
  return h === 'localhost' || h === '127.0.0.1';
}

/**
 * Must match backend `DEV_AUTH_BYPASS_TOKEN` in `.env` (see `.env.example`).
 * Only used on localhost when no JWT access token is in sessionStorage.
 * Set to "" to disable.
 */
export const devAuthBypassToken = '';
