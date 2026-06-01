import { useAuthStore } from "@/features/auth/store";
import { apiFetch } from "@/lib/api/client";

import type { EcgStudyRow } from "./types";

export type { EcgStudyRow, ImageQualityStatus } from "./types";

export const ecgKeys = {
  list: (encounterId: string) => ["ecg-studies", encounterId] as const,
  detail: (encounterId: string, studyId: string) => ["ecg-studies", encounterId, studyId] as const,
};

export async function fetchEcgStudies(encounterId: string): Promise<EcgStudyRow[]> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/ecg-studies`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat studi EKG");
  return body.items as EcgStudyRow[];
}

export async function fetchEcgStudy(encounterId: string, studyId: string): Promise<EcgStudyRow> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/ecg-studies/${studyId}`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat studi EKG");
  return body.study as EcgStudyRow;
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
