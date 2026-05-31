import { apiFetch } from "@/lib/api/client";

export type PredictedClass = "normal" | "mi" | "homi" | "abnormal";
export type AnalysisStatus = "success" | "failed" | "skipped";

export interface AnalysisRow {
  id: number;
  ecg_study_id: number;
  model_metadata_id: number;
  model_name: string;
  architecture: string;
  predicted_class: PredictedClass | null;
  confidence_score: number | null;
  probability_json: Record<string, number>;
  inference_time_ms: number | null;
  device_used: string;
  status: AnalysisStatus;
  error_message: string | null;
  created_at: string;
}

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
