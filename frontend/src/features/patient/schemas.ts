import { z } from "zod";

/** Re-export domain types for backward compatibility (consumers may still
 *  import them from `./schemas`). */
export type {
  DuplicateSuggestion,
  PatientDetail,
  PatientListItem,
  PatientListResponse,
  PatientOut,
  RegisterResponse,
} from "./types";

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
