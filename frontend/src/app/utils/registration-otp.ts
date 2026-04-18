/** Accepted OTP for self-registration (advocate & party in person). */
export const REGISTRATION_DEFAULT_OTP = '0000';

export function isValidRegistrationOtp(value: string | null | undefined): boolean {
  return String(value ?? '').trim() === REGISTRATION_DEFAULT_OTP;
}
