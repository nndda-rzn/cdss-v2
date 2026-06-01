/** Public domain types for the dashboard feature. */

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
