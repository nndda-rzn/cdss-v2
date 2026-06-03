import { apiFetch } from "@/lib/api/client";

import type { AnalysisRow, HiResCAMRow, ModelOption } from "./types";

export type {
  AnalysisRow,
  AnalysisStatus,
  ExplanationStatus,
  HiResCAMRow,
  ModelOption,
  PredictedClass,
} from "./types";

export const modelKeys = {
  list: () => ["models"] as const,
};

export const analysisKeys = {
  list: (encounterId: string, studyId: string) => ["analyses", encounterId, studyId] as const,
};

export async function fetchAnalyses(encounterId: string, studyId: string): Promise<AnalysisRow[]> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/ecg-studies/${studyId}/analyses`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat analisis AI");
  return body.items as AnalysisRow[];
}

export async function fetchModels(): Promise<ModelOption[]> {
  const resp = await apiFetch("/api/models");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat daftar model");
  return body.items as ModelOption[];
}

export async function runAnalysis(
  encounterId: string,
  studyId: string,
  modelIds?: number[],
): Promise<void> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/ecg-studies/${studyId}/analyze`, {
    method: "POST",
    ...(modelIds && modelIds.length > 0
      ? {
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ model_ids: modelIds }),
        }
      : {}),
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.error?.message_id ?? "Gagal menjalankan analisis AI");
  }
}

// ---------------------------------------------------------------------------
// HiResCAM
// ---------------------------------------------------------------------------

export const hirescamKeys = {
  analysis: (encounterId: string, studyId: string, analysisId: string) =>
    ["hirescam", encounterId, studyId, analysisId] as const,
  study: (encounterId: string, studyId: string) =>
    ["hirescam-study", encounterId, studyId] as const,
};

export async function fetchHiResCAM(
  encounterId: string,
  studyId: string,
  analysisId: string,
): Promise<HiResCAMRow | null> {
  const resp = await apiFetch(
    `/api/encounters/${encounterId}/ecg-studies/${studyId}/analyses/${analysisId}/hirescam`,
  );
  if (resp.status === 404) return null;
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat HiResCAM");
  return body.artifact as HiResCAMRow;
}

export async function fetchStudyHiResCAM(
  encounterId: string,
  studyId: string,
): Promise<HiResCAMRow[]> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/ecg-studies/${studyId}/hirescam`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat HiResCAM");
  return body.items as HiResCAMRow[];
}

export async function generateHiResCAM(
  encounterId: string,
  studyId: string,
  analysisId: string,
): Promise<HiResCAMRow> {
  const resp = await apiFetch(
    `/api/encounters/${encounterId}/ecg-studies/${studyId}/analyses/${analysisId}/hirescam`,
    { method: "POST" },
  );
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal generate HiResCAM");
  return body.artifact as HiResCAMRow;
}

export function heatmapUrl(path: string): string {
  // Backend stores paths relative to STORAGE_DIR/heatmaps (e.g. "21/overlay.png")
  // Strip any leading "heatmaps/" for backwards compatibility with old data
  const cleanPath = path.replace(/^heatmaps\//, "");
  return `/api/encounters/heatmaps/${cleanPath}`;
}
