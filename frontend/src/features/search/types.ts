/** Public domain types for the search feature. */

export interface PatientHit {
  id: string;
  mrn: string;
  name_masked: string | null;
  dob: string;
  gender: "male" | "female";
}

export interface EncounterHit {
  id: number;
  patient_id: string;
  encounter_type: "rawat_jalan" | "igd";
  status: "open" | "closed";
  chief_complaint: string | null;
  started_at: string;
}

export interface SearchResults {
  patients: PatientHit[];
  encounters: EncounterHit[];
  query: string;
}
