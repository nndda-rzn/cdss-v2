import { apiFetch } from "@/lib/api/client";

import type { DashboardStats } from "./types";

export type { DashboardStats, RecentEncounter } from "./types";

export const dashboardKeys = {
  stats: () => ["dashboard", "stats"] as const,
};

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const resp = await apiFetch("/api/dashboard/stats");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat dashboard");
  return body as DashboardStats;
}
