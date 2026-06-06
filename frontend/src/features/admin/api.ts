import { apiFetch } from "@/lib/api/client";
import type {
  AdminFacility,
  AdminFacilityListResponse,
  AdminModelListResponse,
  AdminStats,
  AdminUser,
  AdminUserListResponse,
} from "./types";

export const adminKeys = {
  users: ["admin", "users"] as const,
  facilities: ["admin", "facilities"] as const,
  models: ["admin", "models"] as const,
  stats: ["admin", "stats"] as const,
};

export async function fetchUsers(): Promise<AdminUserListResponse> {
  const resp = await apiFetch("/api/admin/users");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to load users");
  return body;
}

export async function createUser(data: {
  name: string;
  email: string;
  password: string;
  role: string;
  facility_id: number;
  profession?: string;
  license_number?: string;
}): Promise<AdminUser> {
  const resp = await apiFetch("/api/admin/users", {
    method: "POST",
    body: JSON.stringify(data),
  });
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to create user");
  return body;
}

export async function updateUser(
  id: number,
  data: Partial<{
    name: string;
    role: string;
    facility_id: number;
    is_active: boolean;
    password: string;
  }>,
): Promise<AdminUser> {
  const resp = await apiFetch(`/api/admin/users/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to update user");
  return body;
}

export async function fetchFacilities(): Promise<AdminFacilityListResponse> {
  const resp = await apiFetch("/api/admin/facilities");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to load facilities");
  return body;
}

export async function createFacility(data: {
  name: string;
  code: string;
  facility_type: string;
  address?: string;
  province_code?: string;
  regency_code?: string;
  subdistrict_code?: string;
}): Promise<AdminFacility> {
  const resp = await apiFetch("/api/admin/facilities", {
    method: "POST",
    body: JSON.stringify(data),
  });
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to create facility");
  return body;
}

export async function updateFacility(
  id: number,
  data: Partial<AdminFacility>,
): Promise<AdminFacility> {
  const resp = await apiFetch(`/api/admin/facilities/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to update facility");
  return body;
}

export async function fetchModels(): Promise<AdminModelListResponse> {
  const resp = await apiFetch("/api/models");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to load models");
  return body;
}

export async function fetchAdminStats(): Promise<AdminStats> {
  const resp = await apiFetch("/api/admin/stats");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to load stats");
  return body;
}
