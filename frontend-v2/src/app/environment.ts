// Align with `frontend` — adjust `url` / port for your API when deploying.

export const url = 'http://localhost';

export const app_url = `${url}:8000`;

export function isLocalDevHost(): boolean {
  if (typeof window === 'undefined') return false;
  const h = window.location.hostname;
  return h === 'localhost' || h === '127.0.0.1';
}

export const devAuthBypassToken = '';

export const sessionProfileKey =
  'hcs_cms_dev_session_profile_key_replace_with_random_in_production_min32';
