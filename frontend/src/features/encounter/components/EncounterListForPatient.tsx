import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { useI18nStore } from "@/lib/i18n/store";
import { Skeleton } from "@/components/ui/skeleton";
import { Stethoscope } from "lucide-react";
import { fetchEncountersByPatient, encounterKeys } from "../api";
import { RoleGate } from "@/features/auth/components/RoleGate";
import { Button } from "@/components/ui/button";
import { FilePlus2 } from "lucide-react";

export function EncounterListForPatient({ patientId }: { patientId: string }) {
  const t = useI18nStore((s) => s.t);
  const { data, isLoading } = useQuery({
    queryKey: encounterKeys.byPatient(patientId),
    queryFn: () => fetchEncountersByPatient(patientId),
    enabled: !!patientId,
  });

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  const encounters = data ?? [];

  if (encounters.length === 0) {
    return (
      <EmptyState
        title={t("Daftar kunjungan akan tampil di sini", "Encounter list will appear here")}
        description={t(
          "Mulai kunjungan baru untuk merekam keluhan, tanda vital, dan studi EKG.",
          "Start a new encounter to record complaints, vitals, and ECG studies.",
        )}
        action={
          <RoleGate allow={["clinician", "nurse"]}>
            <Button asChild size="sm" className="cursor-pointer">
              <Link to={`/patients/${patientId}/encounters/new`}>
                <FilePlus2 className="mr-1.5 h-4 w-4" aria-hidden="true" />
                {t("Kunjungan baru", "New encounter")}
              </Link>
            </Button>
          </RoleGate>
        }
      />
    );
  }

  return (
    <ul className="space-y-2">
      {encounters.map((enc) => (
        <li key={enc.id}>
          <Link
            to={`/encounters/${enc.id}`}
            className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm hover:bg-sunken/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Stethoscope className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
              <span className="font-medium text-foreground">
                {enc.chief_complaint || t("Kunjungan", "Encounter")} #{enc.id}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground tabular">
                {enc.started_at.slice(0, 10)}
              </span>
              <Badge variant={enc.status === "open" ? "default" : "secondary"}>
                {enc.status === "open" ? t("Terbuka", "Open") : t("Selesai", "Closed")}
              </Badge>
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}
