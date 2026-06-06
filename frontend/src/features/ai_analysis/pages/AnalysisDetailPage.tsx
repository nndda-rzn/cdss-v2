import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Printer, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AuthedImage } from "@/components/ui/authed-image";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { PatientIdentityStrip } from "@/components/layout/PatientIdentityStrip";
import { RoleGate } from "@/features/auth/components/RoleGate";
import { ecgKeys, fetchEcgStudy } from "@/features/ecg_study/api";
import { fetchPatient, patientKeys } from "@/features/patient/api";
import { useI18nStore } from "@/lib/i18n/store";
import Zoom from "react-medium-image-zoom";
import "react-medium-image-zoom/dist/styles.css";
import { analysisKeys, fetchAnalyses, fetchStudyHiResCAM, hirescamKeys, runAnalysis } from "../api";
import { AnalysisDetailTable } from "../components/AnalysisDetailTable";
import { ModelSelector } from "../components/ModelSelector";

const CONSENSUS_ID = "consensus-card";

export function AnalysisDetailPage() {
  const { id = "", studyId = "" } = useParams();
  const t = useI18nStore((s) => s.t);
  const qc = useQueryClient();

  const analyses = useQuery({
    queryKey: analysisKeys.list(id, studyId),
    queryFn: () => fetchAnalyses(id, studyId),
    enabled: !!id && !!studyId,
    retry: false,
  });
  const study = useQuery({
    queryKey: ecgKeys.detail(id, studyId),
    queryFn: () => fetchEcgStudy(id, studyId),
    enabled: !!id && !!studyId,
    retry: false,
  });
  const patientId = study.data?.patient_id;
  const patient = useQuery({
    queryKey: patientKeys.detail(patientId ?? ""),
    queryFn: () => fetchPatient(patientId as string),
    enabled: !!patientId,
    retry: false,
  });
  const hirescam = useQuery({
    queryKey: hirescamKeys.study(id, studyId),
    queryFn: () => fetchStudyHiResCAM(id, studyId),
    enabled: !!id && !!studyId,
    retry: false,
  });

  const [selectedModelId, setSelectedModelId] = useState<string>("");

  const mutation = useMutation({
    mutationFn: () =>
      runAnalysis(id, studyId, selectedModelId ? [Number(selectedModelId)] : undefined),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: analysisKeys.list(id, studyId) });
      qc.invalidateQueries({ queryKey: hirescamKeys.study(id, studyId) });
    },
  });

  if (analyses.isError || study.isError) {
    return (
      <EmptyState
        title={t("Akses ditolak", "Access denied")}
        description={t(
          "Peran Anda tidak memiliki izin untuk melihat analisis AI ini.",
          "Your role does not have permission to view this AI analysis.",
        )}
      />
    );
  }

  const rows = analyses.data ?? [];

  return (
    <div className="space-y-5">
      <Link
        to={`/encounters/${id}`}
        className="no-print inline-flex items-center gap-1 text-sm text-primary hover:underline"
      >
        <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
        {t("Kembali ke Kunjungan", "Back to Encounter")} #{id}
      </Link>

      <header className="flex flex-col gap-2">
        {patient.data && <PatientIdentityStrip patient={patient.data} />}
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            {t("Analisis AI", "AI Analysis")}
          </h1>
          <p className="text-sm text-muted-foreground">
            {t("Jalankan analisis AI untuk studi EKG ini.", "Run AI analysis for this ECG study.")}
          </p>
        </div>
      </header>

      {/* Actions */}
      <div className="no-print flex flex-col gap-3 rounded-lg border bg-card p-3 sm:flex-row sm:items-center sm:justify-between">
        <RoleGate allow={["clinical"]}>
          <ModelSelector value={selectedModelId} onChange={setSelectedModelId} />
        </RoleGate>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => window.print()} className="cursor-pointer">
            <Printer className="mr-1.5 h-4 w-4" aria-hidden="true" />
            {t("Cetak", "Print")}
          </Button>
          <RoleGate allow={["clinical"]}>
            <Button
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending || !selectedModelId}
              className="cursor-pointer"
            >
              <Sparkles className="mr-1.5 h-4 w-4" aria-hidden="true" />
              {mutation.isPending
                ? t("Menganalisis...", "Analysing...")
                : rows.length === 0
                  ? t("Jalankan Analisis AI", "Run AI Analysis")
                  : t("Analisis ulang", "Re-run analysis")}
            </Button>
          </RoleGate>
        </div>
      </div>

      {/* ECG + HiResCAM */}
      {study.isLoading ? (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Skeleton variant="ecg" className="h-80 w-full" />
          <Skeleton variant="ecg" className="h-80 w-full" />
        </div>
      ) : (
        study.data && (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card className="overflow-hidden">
              <div className="relative bg-charcoal-50">
                <Zoom>
                  <AuthedImage
                    path={study.data.image_original_path}
                    alt={t("Studi EKG", "ECG study")}
                    className="max-h-[600px] w-full object-contain"
                  />
                </Zoom>
              </div>
              <div className="px-4 py-2 text-xs text-muted-foreground">
                {t("Gambar asli", "Original image")}
              </div>
            </Card>
            {hirescam.isLoading ? (
              <Skeleton variant="ecg" className="h-80 w-full" />
            ) : hirescam.data && hirescam.data.length > 0 ? (
              <Card className="overflow-hidden">
                <div className="relative bg-charcoal-50">
                  <Zoom>
                    <AuthedImage
                      path={`api/encounters/heatmaps/${hirescam.data[0].overlay_path}`}
                      alt={t("Overlay HiResCAM", "HiResCAM overlay")}
                      className="max-h-[600px] w-full object-contain"
                    />
                  </Zoom>
                </div>
                <div className="flex items-center justify-between px-4 py-2 text-xs text-muted-foreground">
                  <span>{t("HiResCAM overlay", "HiResCAM overlay")}</span>
                  <span className="tabular font-medium text-foreground">
                    {t("Fokus", "Focus")}: {Math.round(hirescam.data[0].focus_metric * 100)}%
                  </span>
                </div>
              </Card>
            ) : (
              <Card className="flex items-center justify-center">
                <CardContent className="py-6">
                  <EmptyState
                    title={t("HiResCAM belum tersedia", "HiResCAM not yet available")}
                    description={t(
                      "Jalankan analisis untuk generate penjelasan visual.",
                      "Run analysis to generate visual explanation.",
                    )}
                    hideMotif
                  />
                </CardContent>
              </Card>
            )}
          </div>
        )
      )}

      <Card>
        <CardContent className="overflow-x-auto py-4">
          {analyses.isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : rows.length === 0 ? (
            <EmptyState
              title={t("Belum ada analisis AI", "No AI analysis yet")}
              description={t(
                "Jalankan analisis untuk membandingkan prediksi lima model.",
                "Run the analysis to compare five-model predictions.",
              )}
              hideMotif
            />
          ) : (
            <AnalysisDetailTable
              rows={rows}
              hirescam={hirescam.data}
              describedById={CONSENSUS_ID}
            />
          )}
        </CardContent>
      </Card>

      {mutation.isError && (
        <p role="alert" className="no-print text-sm text-destructive">
          {mutation.error instanceof Error
            ? mutation.error.message
            : t("Gagal menjalankan analisis", "Failed to run analysis")}
        </p>
      )}
    </div>
  );
}
