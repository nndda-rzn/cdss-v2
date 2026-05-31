import { z } from "zod";

export const PatientCreateSchema = z.object({
  name: z.string().min(2, "Nama minimal 2 karakter").max(100),
  dob: z.string().min(1, "Tanggal lahir wajib diisi"),
  gender: z.enum(["male", "female"]),
  nik: z
    .string()
    .regex(/^\d{16}$/, "NIK harus 16 digit")
    .optional()
    .or(z.literal("")),
  phone: z.string().max(30).optional(),
  address: z.string().max(300).optional(),
  consent_data_use: z.literal(true, {
    errorMap: () => ({ message: "Persetujuan penggunaan data wajib" }),
  }),
});

export type PatientCreateValues = z.infer<typeof PatientCreateSchema>;

export interface PatientOut {
  id: string;
  mrn: string;
  name: string;
  dob: string;
  gender: string;
  nik_last4: string | null;
  phone: string | null;
  address: string | null;
  facility_id: number;
}

export interface DuplicateSuggestion {
  id: string;
  mrn: string;
  name_masked: string;
  dob: string;
  gender: string;
}

export interface RegisterResponse {
  patient?: PatientOut;
  duplicates?: DuplicateSuggestion[];
  action: "created" | "confirm";
}

export interface PatientListItem {
  id: string;
  mrn: string;
  name_masked: string;
  dob: string;
  gender: string;
  nik_last4: string | null;
  phone_masked: string | null;
}

export interface PatientListResponse {
  items: PatientListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface PatientDetail {
  id: string;
  mrn?: string;
  name?: string;
  dob: string;
  gender: string;
  nik_last4?: string | null;
  phone?: string | null;
  address?: string | null;
  facility_id: number;
  is_pseudonymized?: boolean;
}
