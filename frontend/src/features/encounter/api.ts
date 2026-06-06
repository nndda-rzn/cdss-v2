import { apiFetch } from "@/lib/api/client";

import type { EncounterCreateInput, EncounterOut } from "./types";

export type { EncounterCreateInput, EncounterOut, EncounterStatus, EncounterType } from "./types";

export const encounterKeys = {
  list: () => ["encounters"] as const,
  detail: (id: number | string) => ["encounter", String(id)] as const,
};

export async function fetchEncounters(): Promise<EncounterOut[]> {
  const resp = await apiFetch("/api/encounters");
  const body = await resp.json();
  if (!resp.ok) {
    throw new Error(body.error?.message_id ?? "Gagal memuat kunjungan");
  }
  return body.items as EncounterOut[];
}

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

export async function fetchEncountersByPatient(patientId: string): Promise<EncounterOut[]> {
  const resp = await apiFetch(`/api/encounters/by-patient/${patientId}`);
  const body = await resp.json();
  if (!resp.ok) {
    throw new Error(body.error?.message_id ?? "Gagal memuat kunjungan");
  }
  return body.items as EncounterOut[];
}
