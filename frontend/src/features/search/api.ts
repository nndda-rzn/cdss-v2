import { apiFetch } from "@/lib/api/client";

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

export async function fetchSearch(q: string): Promise<SearchResults> {
  const resp = await apiFetch(`/api/search?q=${encodeURIComponent(q)}`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat pencarian");
  return body as SearchResults;
}
