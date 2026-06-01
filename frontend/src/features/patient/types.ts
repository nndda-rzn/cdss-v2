/** Public domain types for the patient feature. */

export interface PatientOut {
  id: string;
  mrn: string;
  name: string;
  dob: string;
  gender: string;
  nik_last4: string | null;
  phone: string | null;
  address: string | null;
  facility_id: number;
}

export interface DuplicateSuggestion {
  id: string;
  mrn: string;
  name_masked: string;
  dob: string;
  gender: string;
}

export interface RegisterResponse {
  patient?: PatientOut;
  duplicates?: DuplicateSuggestion[];
  action: "created" | "confirm";
}

export interface PatientListItem {
  id: string;
  mrn: string;
  name_masked: string;
  dob: string;
  gender: string;
  nik_last4: string | null;
  phone_masked: string | null;
}

export interface PatientListResponse {
  items: PatientListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface PatientDetail {
  id: string;
  mrn?: string;
  name?: string;
  dob: string;
  gender: string;
  nik_last4?: string | null;
  phone?: string | null;
  address?: string | null;
  facility_id: number;
  is_pseudonymized?: boolean;
}
