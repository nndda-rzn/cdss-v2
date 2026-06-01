import { differenceInYears, parseISO } from "date-fns";
import { CalendarDays, IdCard, User } from "lucide-react";

import type { PatientDetail } from "@/features/patient/types";
import { useI18nStore } from "@/lib/i18n/store";

function age(dob: string): number | null {
  try {
    return differenceInYears(new Date(), parseISO(dob));
  } catch {
    return null;
  }
}

/**
 * Horizontal patient identity strip for the medical-grade focus header.
 * Mirrors the top-of-screen banner on ECG workstations. Anonymised when the
 * record is pseudonymised (researcher / expert_reviewer reads).
 */
export function PatientIdentityStrip({ patient }: { patient: PatientDetail }) {
  const t = useI18nStore((s) => s.t);
  const yrs = age(patient.dob);
  const genderLabel = patient.gender === "male" ? t("Laki-laki", "Male") : t("Perempuan", "Female");
  const anonymous = patient.is_pseudonymized || !patient.name;

  const ageText = yrs !== null ? `${yrs} ${t("th", "yo")}` : null;

  return (
    <div className="flex min-w-0 items-center gap-2 text-sm">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-affirmed-soft text-primary">
        <User className="h-3.5 w-3.5" aria-hidden="true" />
      </span>
      <div className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-0.5">
        <span className="truncate font-semibold text-foreground">
          {anonymous ? t("Pasien Anonim", "Anonymous Patient") : patient.name}
        </span>
        {!anonymous && patient.mrn && (
          <span className="tabular inline-flex items-center gap-1 text-xs text-muted-foreground">
            <IdCard className="h-3 w-3" aria-hidden="true" />
            {patient.mrn}
          </span>
        )}
        <span className="tabular inline-flex items-center gap-1 text-xs text-muted-foreground">
          <CalendarDays className="h-3 w-3" aria-hidden="true" />
          {patient.dob}
          {ageText ? ` · ${ageText}` : ""} · {genderLabel}
        </span>
      </div>
    </div>
  );
}

PatientIdentityStrip.displayName = "PatientIdentityStrip";
