import { http } from "../../../shared/lib/http";
import type { SessionUser, UserRole } from "../../../shared/types/auth";

interface TokenResponse {
  access: string;
  refresh: string;
}

export type RegisterPartyPayload = {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  date_of_birth: string;
  address: string;
  gender: "M" | "F" | "O" | "U";
};

export type RegisterAdvocatePayload = RegisterPartyPayload & {
  bar_id: string;
  bar_id_file?: File | null;
};

interface LoginPayload {
  email: string;
  password: string;
}

interface VerifyEmailPayload {
  token: string;
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const response = await http.post<TokenResponse>("/accounts/auth/token/", payload);
  return response.data;
}

export async function refreshToken(refresh: string): Promise<TokenResponse> {
  const { data } = await http.post<TokenResponse>("/accounts/auth/token/refresh/", {
    refresh,
  });
  return data;
}

export async function fetchMe(): Promise<SessionUser> {
  const response = await http.get("/accounts/users/me");
  const data = response.data as {
    id: number;
    email: string;
    full_name: string;
    groups: string[];
  };

  return {
    id: data.id,
    email: data.email,
    fullName: data.full_name,
    groups: data.groups,
    role: mapGroupsToRole(data.groups),
  };
}

export async function verifyEmail(payload: VerifyEmailPayload): Promise<void> {
  await http.post("/accounts/auth/verify-email/", payload);
}

export async function registerParty(payload: RegisterPartyPayload): Promise<{ detail: string }> {
  const { data } = await http.post<{ detail: string }>("/accounts/auth/register/party/", payload);
  return data;
}

export async function registerAdvocate(payload: RegisterAdvocatePayload): Promise<{ detail: string }> {
  const formData = new FormData();
  formData.append("email", payload.email);
  formData.append("password", payload.password);
  formData.append("first_name", payload.first_name);
  formData.append("last_name", payload.last_name);
  formData.append("phone_number", payload.phone_number);
  formData.append("date_of_birth", payload.date_of_birth);
  formData.append("address", payload.address);
  formData.append("gender", payload.gender);
  formData.append("bar_id", payload.bar_id);
  if (payload.bar_id_file) formData.append("bar_id_file", payload.bar_id_file);

  const { data } = await http.post<{ detail: string }>("/accounts/auth/register/advocate/", formData);
  return data;
}

function mapGroupsToRole(groups: string[]): UserRole {
  if (groups.includes("PARTY_IN_PERSON")) return "party-in-person";
  if (groups.includes("ADVOCATE")) return "advocate";
  if (groups.includes("SCRUTINY_OFFICER")) return "scrutiny-officers";
  if (groups.includes("LISTING_OFFICER")) return "listing-officers";
  if (groups.includes("JUDGE")) return "judges";
  if (groups.includes("READER")) return "reader";
  if (groups.includes("STENO")) return "steno";
  return "reader";
}
