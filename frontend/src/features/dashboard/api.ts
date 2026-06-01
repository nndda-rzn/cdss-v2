import { apiFetch } from "@/lib/api/client";

export interface RecentEncounter {
  id: number;
  patient_id: string;
  encounter_type: "rawat_jalan" | "igd";
  status: "open" | "closed";
  chief_complaint: string | null;
  started_at: string;
}

export interface DashboardStats {
  total_patients: number;
  active_encounters: number;
  analyses_today: number;
  pending_tasks: number;
  recent_encounters: RecentEncounter[];
}

export const dashboardKeys = {
  stats: () => ["dashboard", "stats"] as const,
};

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const resp = await apiFetch("/api/dashboard/stats");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat dashboard");
  return body as DashboardStats;
}
