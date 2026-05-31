import { apiFetch } from "@/lib/api/client";
import type { PatientCreateValues, RegisterResponse } from "./schemas";

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
