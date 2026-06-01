import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Printer, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { PatientIdentityStrip } from "@/components/layout/PatientIdentityStrip";
import { RoleGate } from "@/features/auth/components/RoleGate";
import { ecgKeys, fetchEcgStudy } from "@/features/ecg_study/api";
import { fetchPatient, patientKeys } from "@/features/patient/api";
import { useI18nStore } from "@/lib/i18n/store";

import { analysisKeys, fetchAnalyses, fetchStudyHiResCAM, hirescamKeys, runAnalysis } from "../api";
import { AnalysisDetailTable } from "../components/AnalysisDetailTable";
import { ConsensusCard } from "../components/ConsensusCard";
import { ExplanationStatusBadge } from "../components/ExplanationStatusBadge";
import { HeatmapViewer } from "../components/HeatmapViewer";
import { StudyHeaderCard } from "../components/StudyHeaderCard";
import type { HiResCAMRow } from "../types";

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

  const mutation = useMutation({
    mutationFn: () => runAnalysis(id, studyId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: analysisKeys.list(id, studyId) });
      qc.invalidateQueries({ queryKey: hirescamKeys.study(id, studyId) });
    },
  });

  // Access denied (403 from either query) -> informative empty state.
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
            {t(
              "Perbandingan lima model YOLO untuk studi EKG ini.",
              "Five-model YOLO comparison for this ECG study.",
            )}
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[3fr_1fr]">
        {study.isLoading ? (
          <Skeleton variant="ecg" className="h-80 w-full" />
        ) : study.data ? (
          <StudyHeaderCard study={study.data} />
        ) : null}
        <ConsensusCard rows={rows} id={CONSENSUS_ID} />
      </div>

      {/* HiResCAM section */}
      {hirescam.data && hirescam.data.length > 0 && (
        <div className="space-y-4">
          <header className="flex items-center justify-between">
            <h2 className="text-lg font-semibold tracking-tight">
              {t("Penjelasan Visual", "Visual Explanation")}
            </h2>
            {hirescam.data[0] && (
              <ExplanationStatusBadge
                status={hirescam.data[0].explanation_status}
                focusMetric={hirescam.data[0].focus_metric}
              />
            )}
          </header>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {hirescam.data.map((hc: HiResCAMRow) => (
              <HeatmapViewer
                key={hc.ai_analysis_id}
                artifact={hc}
                originalPath={study.data?.image_original_path ?? ""}
              />
            ))}
          </div>
        </div>
      )}

      <Card>
        <CardContent className="overflow-x-auto py-4">
          {analyses.isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} variant="ecg" className="h-9 w-full" />
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

      <div className="no-print flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Button asChild variant="outline" className="cursor-pointer">
          <Link to={`/encounters/${id}`}>
            <ArrowLeft className="mr-1.5 h-4 w-4" aria-hidden="true" />
            {t("Kembali", "Back")}
          </Link>
        </Button>
        <Button variant="outline" onClick={() => window.print()} className="cursor-pointer">
          <Printer className="mr-1.5 h-4 w-4" aria-hidden="true" />
          {t("Cetak", "Print")}
        </Button>
        <RoleGate allow={["clinician", "nurse"]}>
          <Button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
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
