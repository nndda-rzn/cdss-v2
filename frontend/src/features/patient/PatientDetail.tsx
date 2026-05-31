import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, FilePlus2, ShieldCheck, Stethoscope } from "lucide-react";
import { ErrorBoundary } from "react-error-boundary";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RoleGate } from "@/features/auth/RoleGate";
import { ConsentPanel } from "@/features/consent/ConsentPanel";
import { HistoryPanel } from "@/features/patient_history/HistoryPanel";

import { fetchPatient, patientKeys } from "./api";
import { DeleteDialog } from "./DeleteDialog";
import { IdentitySidebar } from "./IdentitySidebar";

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
        {error instanceof Error ? error.message : "Gagal memuat"}
      </p>
    );
  }
  if (!data) return null;

  // Researcher / expert_reviewer get an anonymised, sidebar-less variant.
  if (data.is_pseudonymized) {
    return (
      <div className="max-w-lg space-y-4">
        <h1 className="text-xl font-semibold">Detail Pasien</h1>
        <Card>
          <CardHeader
            sectionLabel="Data Anonim"
            sectionIcon={<ShieldCheck className="h-3.5 w-3.5" />}
          >
            <CardTitle>Data ter-anonimisasi</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 border-t border-border-strong pt-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Tanggal Lahir</span>
              <span className="tabular">{data.dob}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Jenis Kelamin</span>
              <span>{data.gender === "male" ? "Laki-laki" : "Perempuan"}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Detail Pasien</h1>
        <RoleGate allow={["admin"]}>
          <DeleteDialog patientId={data.id} />
        </RoleGate>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[320px_1fr]">
        <IdentitySidebar patient={data} />

        <div className="min-w-0">
          <Tabs defaultValue="encounters" className="w-full">
            <TabsList className="rounded-sm">
              <TabsTrigger value="encounters">Kunjungan</TabsTrigger>
              <TabsTrigger value="history">Riwayat Medis</TabsTrigger>
              <TabsTrigger value="consent">Persetujuan</TabsTrigger>
            </TabsList>

            <TabsContent value="encounters" className="mt-3">
              <Card>
                <CardHeader
                  sectionLabel="Kunjungan"
                  sectionIcon={<Stethoscope className="h-3.5 w-3.5" />}
                >
                  <CardTitle>Daftar kunjungan</CardTitle>
                </CardHeader>
                <CardContent className="border-t border-border-strong pt-3">
                  <EmptyState
                    title="Daftar kunjungan akan tampil di sini"
                    description="Mulai kunjungan baru untuk merekam keluhan, tanda vital, dan studi EKG."
                    action={
                      <Button asChild size="sm" className="cursor-pointer">
                        <Link to={`/patients/${data.id}/encounters/new`}>
                          <FilePlus2 className="mr-1.5 h-4 w-4" aria-hidden="true" />
                          Kunjungan baru
                        </Link>
                      </Button>
                    }
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="mt-3">
              <Card>
                <CardHeader
                  sectionLabel="Riwayat"
                  sectionIcon={<Stethoscope className="h-3.5 w-3.5" />}
                >
                  <CardTitle>Riwayat medis</CardTitle>
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
                  sectionLabel="Persetujuan"
                  sectionIcon={<ShieldCheck className="h-3.5 w-3.5" />}
                >
                  <CardTitle>Persetujuan pasien</CardTitle>
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
        Kembali ke daftar
      </Link>
    </div>
  );
}
