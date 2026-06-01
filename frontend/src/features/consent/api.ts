import { apiFetch } from "@/lib/api/client";

import type { ConsentRow, ConsentStatus } from "./types";

export type { ConsentRow, ConsentStatus } from "./types";

export async function fetchConsents(patientId: string): Promise<ConsentRow[]> {
  const resp = await apiFetch(`/api/patients/${patientId}/consent`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat consent");
  return body.items as ConsentRow[];
}

export async function captureConsent(
  patientId: string,
  consentType: string,
  status: ConsentStatus = "given",
): Promise<void> {
  const resp = await apiFetch(`/api/patients/${patientId}/consent`, {
    method: "POST",
    body: JSON.stringify({ consent_type: consentType, status }),
  });
  if (!resp.ok) {
    const body = await resp.json();
    throw new Error(body.error?.message_id ?? "Gagal menyimpan consent");
  }
}

export const consentKeys = {
  list: (patientId: string) => ["consent", patientId] as const,
};
