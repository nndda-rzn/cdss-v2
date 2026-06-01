/** Public domain types for the consent feature. */

export interface ConsentRow {
  id: number;
  consent_type: string;
  status: string;
  given_at: string | null;
  revoked_at: string | null;
}

export type ConsentStatus = "given" | "revoked";
