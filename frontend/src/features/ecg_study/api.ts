import { useAuthStore } from "@/features/auth/store";
import { apiFetch } from "@/lib/api/client";

export interface EcgStudyRow {
  id: number;
  encounter_id: number;
  patient_id?: string;
  study_uid: string;
  image_original_path: string;
  image_processed_path: string | null;
  image_quality_status: "good" | "acceptable" | "poor";
  image_quality_score: number;
  image_quality_metrics_json: Record<string, number>;
  acquired_at: string;
  recorded_by_user_id: number;
  device_info?: string | null;
  created_at: string;
}

export const ecgKeys = {
  list: (encounterId: string) => ["ecg-studies", encounterId] as const,
};

export async function fetchEcgStudies(encounterId: string): Promise<EcgStudyRow[]> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/ecg-studies`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat studi EKG");
  return body.items as EcgStudyRow[];
}

export async function uploadEcgStudy(
  encounterId: string,
  file: File,
  deviceInfo?: string,
): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  if (deviceInfo) form.append("device_info", deviceInfo);

  const { accessToken } = useAuthStore.getState();
  const headers: Record<string, string> = {};
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  const resp = await fetch(`/api/encounters/${encounterId}/ecg-studies`, {
    method: "POST",
    headers,
    body: form,
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.error?.message_id ?? "Gagal mengunggah EKG");
  }
}
