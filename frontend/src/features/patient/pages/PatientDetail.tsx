import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ShieldCheck, Stethoscope } from "lucide-react";
import { ErrorBoundary } from "react-error-boundary";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RoleGate } from "@/features/auth/components/RoleGate";
import { ConsentPanel } from "@/features/consent/components/ConsentPanel";
import { HistoryPanel } from "@/features/patient_history/components/HistoryPanel";
import { useI18nStore } from "@/lib/i18n/store";

import { fetchPatient, patientKeys } from "../api";
import { DeleteDialog } from "../components/DeleteDialog";
import { IdentitySidebar } from "../components/IdentitySidebar";
import { EncounterListForPatient } from "@/features/encounter/components/EncounterListForPatient";

function PanelFallback({ error }: { error: unknown }) {
  const message = error instanceof Error ? error.message : "Tidak dapat memuat panel";
  return (
    <p role="alert" className="text-sm text-destructive">
      {message}
    </p>
  );
}

export function PatientDetail() {
  const { id = "" } = useParams();
  const t = useI18nStore((s) => s.t);
  const { data, isLoading, isError, error } = useQuery({
    queryKey: patientKeys.detail(id),
    queryFn: () => fetchPatient(id),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[320px_1fr]">
        <Skeleton className="h-72 w-full" />
        <Skeleton variant="ecg" className="h-72 w-full" />
      </div>
    );
  }
  if (isError) {
    return (
      <p role="alert" className="text-sm text-destructive">
        {error instanceof Error ? error.message : t("Gagal memuat", "Failed to load")}
      </p>
    );
  }
  if (!data) return null;

  // Researcher / expert_reviewer get an anonymised, sidebar-less variant.
  if (data.is_pseudonymized) {
    return (
      <div className="max-w-lg space-y-4">
        <h1 className="text-xl font-semibold">{t("Detail Pasien", "Patient Detail")}</h1>
        <Card>
          <CardHeader
            sectionLabel={t("Data Anonim", "Anonymised Data")}
            sectionIcon={<ShieldCheck className="h-3.5 w-3.5" />}
          >
            <CardTitle>{t("Data ter-anonimisasi", "Anonymised data")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 border-t border-border-strong pt-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("Tanggal Lahir", "Date of Birth")}</span>
              <span className="tabular">{data.dob}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("Jenis Kelamin", "Gender")}</span>
              <span>
                {data.gender === "male" ? t("Laki-laki", "Male") : t("Perempuan", "Female")}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{t("Detail Pasien", "Patient Detail")}</h1>
        <RoleGate allow={["admin"]}>
          <DeleteDialog patientId={data.id} />
        </RoleGate>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[320px_1fr]">
        <IdentitySidebar patient={data} />

        <div className="min-w-0">
          <Tabs defaultValue="encounters" className="w-full">
            <TabsList className="rounded-sm">
              <TabsTrigger value="encounters">{t("Kunjungan", "Encounters")}</TabsTrigger>
              <TabsTrigger value="history">{t("Riwayat Medis", "Medical History")}</TabsTrigger>
              <TabsTrigger value="consent">{t("Persetujuan", "Consent")}</TabsTrigger>
            </TabsList>

            <TabsContent value="encounters" className="mt-3">
              <Card>
                <CardHeader
                  sectionLabel={t("Kunjungan", "Encounters")}
                  sectionIcon={<Stethoscope className="h-3.5 w-3.5" />}
                >
                  <CardTitle>{t("Daftar kunjungan", "Encounter list")}</CardTitle>
                </CardHeader>
                <CardContent className="border-t border-border-strong pt-3">
                  <EncounterListForPatient patientId={data.id} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="mt-3">
              <Card>
                <CardHeader
                  sectionLabel={t("Riwayat", "History")}
                  sectionIcon={<Stethoscope className="h-3.5 w-3.5" />}
                >
                  <CardTitle>{t("Riwayat medis", "Medical history")}</CardTitle>
                </CardHeader>
                <CardContent className="border-t border-border-strong pt-3">
                  <ErrorBoundary FallbackComponent={PanelFallback}>
                    <HistoryPanel patientId={data.id} />
                  </ErrorBoundary>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="consent" className="mt-3">
              <Card>
                <CardHeader
                  sectionLabel={t("Persetujuan", "Consent")}
                  sectionIcon={<ShieldCheck className="h-3.5 w-3.5" />}
                >
                  <CardTitle>{t("Persetujuan pasien", "Patient consent")}</CardTitle>
                </CardHeader>
                <CardContent className="border-t border-border-strong pt-3">
                  <ErrorBoundary FallbackComponent={PanelFallback}>
                    <ConsentPanel patientId={data.id} />
                  </ErrorBoundary>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      <Link
        to="/patients"
        className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
      >
        <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
        {t("Kembali ke daftar", "Back to list")}
      </Link>
    </div>
  );
}
