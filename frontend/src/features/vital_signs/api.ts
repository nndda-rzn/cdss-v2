import { apiFetch } from "@/lib/api/client";

export interface VitalRow {
  id: number;
  measured_at: string;
  bp_systolic: number | null;
  bp_diastolic: number | null;
  heart_rate: number | null;
  respiratory_rate: number | null;
  spo2: number | null;
  temperature: number | null;
  weight: number | null;
  height: number | null;
}

export type VitalsInput = Partial<Omit<VitalRow, "id" | "measured_at">>;

export const vitalsKeys = {
  list: (encounterId: string) => ["vitals", encounterId] as const,
};

export async function fetchVitals(encounterId: string): Promise<VitalRow[]> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/vital-signs`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat vital");
  return body.items as VitalRow[];
}

export async function captureVitals(encounterId: string, input: VitalsInput): Promise<void> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/vital-signs`, {
    method: "POST",
    body: JSON.stringify(input),
  });
  if (!resp.ok) {
    const body = await resp.json();
    throw new Error(body.error?.message_id ?? "Gagal menyimpan vital");
  }
}
