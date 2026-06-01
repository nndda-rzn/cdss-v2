import { differenceInYears, parseISO } from "date-fns";
import { User } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { PatientDetail } from "@/features/patient/types";
import { useI18nStore } from "@/lib/i18n/store";

function initials(name: string | null | undefined): string {
  if (!name) return "·";
  const words = name.trim().split(/\s+/);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[words.length - 1][0]).toUpperCase();
}

function ageOf(dob: string): number | null {
  try {
    return differenceInYears(new Date(), parseISO(dob));
  } catch {
    return null;
  }
}

interface EncounterPatientBannerProps {
  patient: PatientDetail | undefined;
  encounterId: number;
  status: string;
}

/**
 * Sticky EMR-style patient banner pinned at the top of the encounter detail
 * page: avatar + masked identity on the left, encounter number + status on
 * the right. Anonymised for pseudonymised reads.
 */
export function EncounterPatientBanner({
  patient,
  encounterId,
  status,
}: EncounterPatientBannerProps) {
  const t = useI18nStore((s) => s.t);
  const anonymous = !patient || patient.is_pseudonymized || !patient.name;
  const age = patient ? ageOf(patient.dob) : null;
  const genderLabel = patient
    ? patient.gender === "male"
      ? t("Laki-laki", "Male")
      : t("Perempuan", "Female")
    : "";

  return (
    <div className="sticky top-0 z-20 flex h-14 items-center gap-3 rounded-lg border border-border-strong bg-paper px-4 shadow-elev-sm">
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-affirmed-soft text-xs font-semibold text-primary">
        {anonymous ? <User className="h-4 w-4" aria-hidden="true" /> : initials(patient?.name)}
      </span>

      <div className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-0 text-sm">
        <span className="truncate font-semibold text-foreground">
          {anonymous ? t("Pasien Anonim", "Anonymous Patient") : patient?.name}
        </span>
        {!anonymous && patient?.mrn && (
          <span className="tabular text-xs text-muted-foreground">{patient.mrn}</span>
        )}
        {patient && (
          <span className="tabular text-xs text-muted-foreground">
            {patient.dob}
            {age !== null ? ` · ${age} ${t("th", "yo")}` : ""} · {genderLabel}
          </span>
        )}
      </div>

      <div className="ml-auto flex shrink-0 items-center gap-2">
        <span className="tabular text-sm font-medium text-foreground">
          {t("Kunjungan", "Encounter")} #{encounterId}
        </span>
        <Badge variant={status === "open" ? "default" : "secondary"}>
          {status === "open" ? t("Aktif", "Open") : t("Tertutup", "Closed")}
        </Badge>
      </div>
    </div>
  );
}
