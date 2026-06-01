/** Public domain types for the encounter feature. */

export type EncounterType = "rawat_jalan" | "igd";

export type EncounterStatus = "open" | "closed";

export interface EncounterOut {
  id: number;
  patient_id: string;
  facility_id: number;
  attending_user_id: number;
  encounter_type: string;
  status: string;
  chief_complaint: string | null;
  started_at: string;
  ended_at: string | null;
}

export interface EncounterCreateInput {
  patient_id: string;
  encounter_type: EncounterType;
  chief_complaint?: string;
}
