import { apiFetch } from "@/lib/api/client";
import type {
  PatientCreateValues,
  PatientDetail,
  PatientListResponse,
  RegisterResponse,
} from "./schemas";

export const patientKeys = {
  all: ["patients"] as const,
  list: (params: Record<string, string>) => [...patientKeys.all, "list", params] as const,
  detail: (id: string) => [...patientKeys.all, "detail", id] as const,
};

function toPayload(values: PatientCreateValues) {
  return {
    name: values.name,
    dob: values.dob,
    gender: values.gender,
    nik: values.nik ? values.nik : undefined,
    phone: values.phone ? values.phone : undefined,
    address: values.address ? values.address : undefined,
    consent_data_use: values.consent_data_use,
  };
}

export async function registerPatient(
  values: PatientCreateValues,
  options: { confirmNew?: boolean } = {},
): Promise<RegisterResponse> {
  const url = options.confirmNew ? "/api/patients?confirm_new=true" : "/api/patients";
  const resp = await apiFetch(url, {
    method: "POST",
    body: JSON.stringify(toPayload(values)),
  });
  const body = await resp.json();
  if (!resp.ok) {
    throw new Error(body.error?.message_id ?? "Registrasi gagal");
  }
  return body as RegisterResponse;
}

export async function fetchPatients(
  params: Record<string, string> = {},
): Promise<PatientListResponse> {
  const qs = new URLSearchParams(params).toString();
  const resp = await apiFetch(`/api/patients${qs ? `?${qs}` : ""}`);
  const body = await resp.json();
  if (!resp.ok) {
    throw new Error(body.error?.message_id ?? "Gagal memuat pasien");
  }
  return body as PatientListResponse;
}

export async function fetchPatient(id: string): Promise<PatientDetail> {
  const resp = await apiFetch(`/api/patients/${id}`);
  const body = await resp.json();
  if (!resp.ok) {
    throw new Error(body.error?.message_id ?? "Gagal memuat detail pasien");
  }
  return body as PatientDetail;
}

export async function deletePatient(id: string, reason: string): Promise<void> {
  const resp = await apiFetch(`/api/patients/${id}`, {
    method: "DELETE",
    body: JSON.stringify({ reason }),
  });
  if (!resp.ok) {
    const body = await resp.json();
    throw new Error(body.error?.message_id ?? "Gagal menghapus pasien");
  }
}
