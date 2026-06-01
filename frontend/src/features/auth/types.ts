/** Public domain types for the auth feature. */

export interface LoginInput {
  email: string;
  password: string;
}

export interface AuthUser {
  id: number;
  name: string;
  role: string;
}

/** Subset of JWT claims we read on the client (display only — never used to
 *  enforce authorization). */
export interface JwtClaims {
  sub?: string;
  role?: string;
  facility_id?: number;
  email?: string;
}
