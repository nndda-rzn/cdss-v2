import { apiFetch } from "@/lib/api/client";

import type { HistoryRow } from "./types";

export type { HistoryRow } from "./types";

export async function fetchHistory(patientId: string): Promise<HistoryRow[]> {
  const resp = await apiFetch(`/api/patients/${patientId}/history`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat riwayat");
  return body.items as HistoryRow[];
}

export async function addHistory(
  patientId: string,
  conditionCode: string,
  note?: string,
): Promise<void> {
  const resp = await apiFetch(`/api/patients/${patientId}/history`, {
    method: "POST",
    body: JSON.stringify({ condition_code: conditionCode, note }),
  });
  if (!resp.ok) {
    const body = await resp.json();
    throw new Error(body.error?.message_id ?? "Gagal menyimpan riwayat");
  }
}

export const historyKeys = {
  list: (patientId: string) => ["history", patientId] as const,
};
