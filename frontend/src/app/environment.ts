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

/**
 * Passphrase for AES-GCM encryption of the user profile blob in sessionStorage (`user_session_enc`).
 * Replace with a long random value per deployment; empty string disables encryption (cache only).
 * This does not stop a determined attacker with the built JS—only casual DevTools inspection.
 */
export const sessionProfileKey =
  'hcs_cms_dev_session_profile_key_replace_with_random_in_production_min32';
