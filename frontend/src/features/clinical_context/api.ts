import { apiFetch } from "@/lib/api/client";

import type { ClinicalContextInput, ClinicalContextOut } from "./types";

export type { ClinicalContextInput, ClinicalContextOut } from "./types";

export const contextKeys = {
  detail: (encounterId: string) => ["clinical-context", encounterId] as const,
};

export async function fetchContext(encounterId: string): Promise<ClinicalContextOut | null> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/clinical-context`);
  if (resp.status === 404) return null;
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat konteks");
  return body as ClinicalContextOut;
}

export async function saveContext(encounterId: string, input: ClinicalContextInput): Promise<void> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/clinical-context`, {
    method: "POST",
    body: JSON.stringify(input),
  });
  if (!resp.ok) {
    const body = await resp.json();
    throw new Error(body.error?.message_id ?? "Gagal menyimpan konteks");
  }
}
