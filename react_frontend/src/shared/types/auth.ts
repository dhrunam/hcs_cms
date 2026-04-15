export type UserRole =
  | "party-in-person"
  | "advocate"
  | "scrutiny-officers"
  | "listing-officers"
  | "judges"
  | "reader"
  | "steno";

export interface SessionUser {
  id: number;
  email: string;
  fullName: string;
  groups: string[];
  role: UserRole;
}
