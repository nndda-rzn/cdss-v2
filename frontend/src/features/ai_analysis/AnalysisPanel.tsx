import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";

import { analysisKeys, fetchAnalyses, runAnalysis } from "./api";
import { AnalysisTable } from "./AnalysisTable";
import { computeConsensus } from "./labels";

export function AnalysisPanel({ encounterId, studyId }: { encounterId: string; studyId: string }) {
  const qc = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: analysisKeys.list(encounterId, studyId),
    queryFn: () => fetchAnalyses(encounterId, studyId),
  });

  const mutation = useMutation({
    mutationFn: () => runAnalysis(encounterId, studyId),
    onSuccess: () => {
      setError(null);
      qc.invalidateQueries({ queryKey: analysisKeys.list(encounterId, studyId) });
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Gagal"),
  });

  if (isLoading) {
    return <p className="text-xs text-muted-foreground">Memuat analisis...</p>;
  }

  const rows = data ?? [];

  if (rows.length === 0) {
    return (
      <div className="space-y-2">
        <EmptyState
          title="Belum ada analisis AI"
          description="Jalankan analisis untuk membandingkan prediksi dari lima model."
          hideMotif
          action={
            <Button
              size="sm"
              disabled={mutation.isPending}
              onClick={() => mutation.mutate()}
              className="cursor-pointer"
            >
              {mutation.isPending ? "Menganalisis..." : "Jalankan Analisis AI"}
            </Button>
          }
        />
        {error && (
          <p role="alert" className="text-xs text-destructive">
            {error}
          </p>
        )}
      </div>
    );
  }

  const consensus = computeConsensus(rows);

  return (
    <div className="space-y-3">
      {consensus && (
        <p className="text-xs text-muted-foreground">
          Konsensus: <span className="font-semibold text-foreground">{consensus.label}</span>{" "}
          <span className="tabular">
            ({consensus.count}/{consensus.total} model)
          </span>
        </p>
      )}

      <AnalysisTable rows={rows} />

      {error && (
        <p role="alert" className="text-xs text-destructive">
          {error}
        </p>
      )}

      <Button
        size="sm"
        variant="outline"
        disabled={mutation.isPending}
        onClick={() => mutation.mutate()}
        className="cursor-pointer"
      >
        {mutation.isPending ? "Menganalisis..." : "Analisis ulang"}
      </Button>
    </div>
  );
}
