import { apiFetch } from "@/lib/api/client";

import type { AnalysisRow } from "./types";

export type { AnalysisRow, AnalysisStatus, PredictedClass } from "./types";

export const analysisKeys = {
  list: (encounterId: string, studyId: string) => ["analyses", encounterId, studyId] as const,
};

export async function fetchAnalyses(encounterId: string, studyId: string): Promise<AnalysisRow[]> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/ecg-studies/${studyId}/analyses`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat analisis AI");
  return body.items as AnalysisRow[];
}

export async function runAnalysis(encounterId: string, studyId: string): Promise<void> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/ecg-studies/${studyId}/analyze`, {
    method: "POST",
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.error?.message_id ?? "Gagal menjalankan analisis AI");
  }
}
