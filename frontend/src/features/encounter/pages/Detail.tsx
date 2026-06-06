import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ContextForm } from "@/features/clinical_context/components/ContextForm";
import { EcgStudyList } from "@/features/ecg_study/components/EcgStudyList";
import { EcgUploadForm } from "@/features/ecg_study/components/EcgUploadForm";
import { fetchPatient, patientKeys } from "@/features/patient/api";
import { VitalsPanel } from "@/features/vital_signs/components/VitalsPanel";
import { useI18nStore } from "@/lib/i18n/store";

import { closeEncounter, encounterKeys, fetchEncounter } from "../api";
import { EncounterActionsCard } from "../components/EncounterActionsCard";
import { EncounterInfoCard } from "../components/EncounterInfoCard";
import { EncounterPatientBanner } from "../components/EncounterPatientBanner";
import { EncounterPatientCard } from "../components/EncounterPatientCard";

export function Detail() {
  const { id = "" } = useParams();
  const t = useI18nStore((s) => s.t);
  const qc = useQueryClient();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: encounterKeys.detail(id),
    queryFn: () => fetchEncounter(id),
    enabled: !!id,
  });

  const patientId = data?.patient_id;
  const patient = useQuery({
    queryKey: patientKeys.detail(patientId ?? ""),
    queryFn: () => fetchPatient(patientId as string),
    enabled: !!patientId,
    retry: false,
  });

  const closeMutation = useMutation({
    mutationFn: () => closeEncounter(Number(id)),
    onSuccess: () => qc.invalidateQueries({ queryKey: encounterKeys.detail(id) }),
  });

  if (isLoading) return <Skeleton className="h-48 w-full" />;
  if (isError) {
    return (
      <p role="alert" className="text-sm text-destructive">
        {error instanceof Error ? error.message : "Gagal memuat"}
      </p>
    );
  }
  if (!data) return null;

  return (
    <div className="space-y-4">
      <EncounterPatientBanner patient={patient.data} encounterId={data.id} status={data.status} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_320px]">
        {/* Clinical content */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t("Tanda Vital", "Vital Signs")}</CardTitle>
            </CardHeader>
            <CardContent className="p-5 pt-4">
              <VitalsPanel encounterId={String(data.id)} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("Konteks Klinis", "Clinical Context")}</CardTitle>
            </CardHeader>
            <CardContent className="p-5 pt-4">
              <ContextForm encounterId={String(data.id)} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("Studi EKG", "ECG Studies")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 p-5 pt-4">
              <EcgUploadForm encounterId={String(data.id)} />
              <EcgStudyList encounterId={String(data.id)} />
            </CardContent>
          </Card>
        </div>

        {/* Meta rail */}
        <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <EncounterInfoCard
            encounterType={data.encounter_type}
            startedAt={data.started_at}
            chiefComplaint={data.chief_complaint}
          />
          <EncounterActionsCard
            status={data.status}
            patientId={data.patient_id}
            closing={closeMutation.isPending}
            onClose={() => closeMutation.mutate()}
          />
          {patient.data && <EncounterPatientCard patient={patient.data} />}
        </aside>
      </div>
    </div>
  );
}
