import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { PatientDetail } from "@/features/patient/types";
import { useI18nStore } from "@/lib/i18n/store";

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3 border-b border-border py-1.5 last:border-0">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right text-foreground">{value}</span>
    </div>
  );
}

/** Rail card: patient summary + link to the full profile. */
export function EncounterPatientCard({ patient }: { patient: PatientDetail }) {
  const t = useI18nStore((s) => s.t);
  const anonymous = patient.is_pseudonymized || !patient.name;

  return (
    <Card>
      <CardHeader className="p-4 pb-2" sectionLabel={t("Pasien", "Patient")} />
      <CardContent className="p-4 pt-0 text-sm">
        <Row label={t("Tanggal Lahir", "Date of Birth")} value={patient.dob} />
        {!anonymous && patient.phone != null && (
          <Row label={t("Telepon", "Phone")} value={patient.phone} />
        )}
        {!anonymous && patient.address != null && (
          <Row label={t("Alamat", "Address")} value={patient.address} />
        )}
        <Link
          to={`/patients/${patient.id}`}
          className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
        >
          {t("Profil Pasien", "Patient Profile")}
          <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
        </Link>
      </CardContent>
    </Card>
  );
}
