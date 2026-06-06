export interface AdminUser {
  id: number;
  name: string;
  email: string;
  role: string;
  facility_id: number;
  is_active: boolean;
  profession: string | null;
  license_number: string | null;
}

export interface AdminFacility {
  id: number;
  name: string;
  code: string;
  facility_type: string;
  address: string | null;
  province_code: string | null;
  regency_code: string | null;
  subdistrict_code: string | null;
  is_active: boolean;
}

export interface AdminUserListResponse {
  items: AdminUser[];
}

export interface AdminFacilityListResponse {
  items: AdminFacility[];
}

export interface AdminAiStats {
  analyses_today: number;
  yesterday: number;
  avg_inference_ms: number;
  avg_confidence: number;
  inference_trend: { date: string; avg_ms: number | null }[];
  confidence_trend: { date: string; avg: number | null }[];
}

export interface AdminAuditEntry {
  user_id: number | null;
  action: string;
  entity_type: string | null;
  entity_id: number | null;
  created_at: string | null;
}

export interface AdminModel {
  id: number;
  model_name: string;
  model_version: string;
  architecture: string;
  task_type: string;
  input_size: number;
  model_file_path: string;
  model_checksum: string;
  model_size_mb: number;
  class_names_json: string[];
  threshold_config_json: Record<string, unknown>;
  is_active: boolean;
  training_date: string | null;
  created_at: string;
}

export interface AdminModelListResponse {
  items: AdminModel[];
}

export interface AdminStats {
  users: { total: number; active: number; by_role: Record<string, number> };
  facilities: { total: number };
  sessions: { active: number };
  model: { name: string | null; version: string | null; is_active: boolean };
  patients: { total: number };
  encounters: { today: number; yesterday: number };
  ecg: { today: number; yesterday: number };
  ai: AdminAiStats;
  audit: AdminAuditEntry[];
}
