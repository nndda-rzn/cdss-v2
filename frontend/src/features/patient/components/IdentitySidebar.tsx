import { differenceInYears, parseISO } from "date-fns";
import { Calendar, IdCard, MapPin, Phone, User } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface Patient {
  id: string;
  mrn?: string;
  name?: string;
  dob: string;
  gender: string;
  nik_last4?: string | null;
  phone?: string | null;
  address?: string | null;
  is_pseudonymized?: boolean;
}

interface IdentitySidebarProps {
  patient: Patient;
  className?: string;
}

/* Deterministic palette pick from a UUID hash, so a given patient always
 * gets the same avatar tone. 6 muted petrol/charcoal tones. */
const AVATAR_TONES = [
  "bg-petrol-100 text-petrol-700",
  "bg-petrol-200 text-petrol-800",
  "bg-charcoal-100 text-charcoal-700",
  "bg-charcoal-200 text-charcoal-800",
  "bg-affirmed-soft text-primary",
  "bg-amber-50 text-amber-700",
] as const;

function pickTone(uuid: string): string {
  let sum = 0;
  for (const ch of uuid) sum = (sum * 31 + ch.charCodeAt(0)) >>> 0;
  return AVATAR_TONES[sum % AVATAR_TONES.length];
}

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

function Field({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof User;
  label: string;
  value: string | null | undefined;
}) {
  return (
    <div className="flex items-start gap-2 py-1.5 text-sm">
      <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
      <div className="flex flex-1 flex-col gap-0.5">
        <span className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</span>
        <span className="text-foreground">{value ?? "-"}</span>
      </div>
    </div>
  );
}

export function IdentitySidebar({ patient, className }: IdentitySidebarProps) {
  const tone = pickTone(patient.id);
  const age = ageOf(patient.dob);
  const genderLabel = patient.gender === "male" ? "Laki-laki" : "Perempuan";

  return (
    <Card className={cn("sticky top-4 self-start", className)}>
      <CardHeader sectionLabel="Identitas Pasien" sectionIcon={<User className="h-3.5 w-3.5" />}>
        <div className="mt-2 flex items-center gap-3">
          <Avatar className={cn("h-12 w-12 rounded-sm text-base font-semibold", tone)}>
            <AvatarFallback className={tone}>{initials(patient.name)}</AvatarFallback>
          </Avatar>
          <div className="flex flex-col">
            <span className="text-sm font-semibold leading-tight text-foreground">
              {patient.name ?? "Anonim"}
            </span>
            <span className="tabular text-xs text-muted-foreground">MRN {patient.mrn}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="border-t border-border-strong pt-3">
        <Field
          icon={Calendar}
          label="Tanggal lahir"
          value={`${patient.dob}${age !== null ? ` (${age} thn)` : ""}`}
        />
        <Field icon={User} label="Jenis kelamin" value={genderLabel} />
        <Field
          icon={IdCard}
          label="NIK (4 digit)"
          value={
            patient.nik_last4
              ? `\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022 ${patient.nik_last4}`
              : null
          }
        />
        <Field icon={Phone} label="Telepon" value={patient.phone} />
        <Field icon={MapPin} label="Alamat" value={patient.address} />
      </CardContent>
    </Card>
  );
}

IdentitySidebar.displayName = "IdentitySidebar";
