import { apiFetch } from "@/lib/api/client";

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
  encounter_type: "rawat_jalan" | "igd";
  chief_complaint?: string;
}

export const encounterKeys = {
  detail: (id: number | string) => ["encounter", String(id)] as const,
};

export async function createEncounter(input: EncounterCreateInput): Promise<EncounterOut> {
  const resp = await apiFetch("/api/encounters", {
    method: "POST",
    body: JSON.stringify(input),
  });
  const body = await resp.json();
  if (!resp.ok) {
    throw new Error(body.error?.message_id ?? "Gagal membuat kunjungan");
  }
  return body.encounter as EncounterOut;
}

export async function fetchEncounter(id: string): Promise<EncounterOut> {
  const resp = await apiFetch(`/api/encounters/${id}`);
  const body = await resp.json();
  if (!resp.ok) {
    throw new Error(body.error?.message_id ?? "Gagal memuat kunjungan");
  }
  return body as EncounterOut;
}

export async function closeEncounter(id: number): Promise<void> {
  const resp = await apiFetch(`/api/encounters/${id}/close`, {
    method: "PATCH",
  });
  if (!resp.ok) {
    const body = await resp.json();
    throw new Error(body.error?.message_id ?? "Gagal menutup kunjungan");
  }
}
