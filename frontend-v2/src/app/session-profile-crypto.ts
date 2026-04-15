/**
 * Client-side AES-GCM encryption for a small user profile JSON in sessionStorage.
 */

import { sessionProfileKey as envSessionProfileKey } from './environment';

export const USER_SESSION_ENC_KEY = 'user_session_enc';

export interface UserSessionProfile {
  displayName: string;
  groups: string[];
  email?: string;
  username?: string;
  registration_type?: string;
}

const PBKDF2_ITERATIONS = 100_000;
const SALT_BYTES = 16;
const IV_BYTES = 12;

function uint8ToBase64(bytes: Uint8Array): string {
  let s = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    s += String.fromCharCode(bytes[i]);
  }
  return btoa(s);
}

function base64ToUint8(b64: string): Uint8Array {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) {
    out[i] = bin.charCodeAt(i);
  }
  return out;
}

async function deriveAesKey(passphrase: string, salt: Uint8Array): Promise<CryptoKey> {
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    enc.encode(passphrase),
    'PBKDF2',
    false,
    ['deriveBits', 'deriveKey'],
  );
  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: Uint8Array.from(salt),
      iterations: PBKDF2_ITERATIONS,
      hash: 'SHA-256',
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt'],
  );
}

export async function encryptUserSessionProfile(
  profile: UserSessionProfile,
  passphrase: string,
): Promise<string | null> {
  const key = passphrase?.trim();
  if (!key) {
    return null;
  }
  try {
    const salt = crypto.getRandomValues(new Uint8Array(SALT_BYTES));
    const iv = crypto.getRandomValues(new Uint8Array(IV_BYTES));
    const aesKey = await deriveAesKey(key, salt);
    const enc = new TextEncoder();
    const plaintext = enc.encode(JSON.stringify(profile));
    const ciphertext = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv: Uint8Array.from(iv) },
      aesKey,
      plaintext,
    );
    const envelope = {
      v: 1 as const,
      salt: uint8ToBase64(salt),
      iv: uint8ToBase64(iv),
      ct: uint8ToBase64(new Uint8Array(ciphertext)),
    };
    return JSON.stringify(envelope);
  } catch {
    return null;
  }
}

export async function decryptUserSessionProfile(
  stored: string,
  passphrase: string,
): Promise<UserSessionProfile | null> {
  const key = passphrase?.trim();
  if (!key || !stored) {
    return null;
  }
  try {
    const envelope = JSON.parse(stored) as { v: number; salt: string; iv: string; ct: string };
    if (envelope.v !== 1) {
      return null;
    }
    const salt = base64ToUint8(envelope.salt);
    const iv = base64ToUint8(envelope.iv);
    const ct = base64ToUint8(envelope.ct);
    const aesKey = await deriveAesKey(key, salt);
    const plaintext = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: Uint8Array.from(iv) },
      aesKey,
      Uint8Array.from(ct),
    );
    const text = new TextDecoder().decode(plaintext);
    return JSON.parse(text) as UserSessionProfile;
  } catch {
    return null;
  }
}

export function isSessionProfileEncryptionConfigured(): boolean {
  return !!envSessionProfileKey?.trim();
}
