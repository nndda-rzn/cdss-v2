import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

import {
  analysisKeys,
  fetchAnalyses,
  runAnalysis,
  type AnalysisRow,
  type PredictedClass,
} from "./api";

const CLASS_LABEL: Record<PredictedClass, string> = {
  normal: "Normal",
  mi: "Infark Miokard (MI)",
  homi: "Riwayat MI",
  abnormal: "Aritmia/Abnormal",
};

const CLASS_CHIP: Record<PredictedClass, string> = {
  normal: "bg-affirmed-soft text-primary",
  abnormal: "bg-caution-soft text-amber-700",
  mi: "bg-negative-soft text-wine-700",
  homi: "bg-negative-soft text-wine-700 ring-1 ring-inset ring-wine-700/30",
};

function PredictionChip({ value }: { value: PredictedClass }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-medium",
        CLASS_CHIP[value],
      )}
    >
      {CLASS_LABEL[value]}
    </span>
  );
}

function ConfidenceBar({ value }: { value: number | null }) {
  if (value === null) return <span className="text-xs text-muted-foreground">-</span>;
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-full max-w-[120px] overflow-hidden rounded-full bg-sunken">
        <div className="h-full rounded-full bg-petrol-600" style={{ width: `${value * 100}%` }} />
      </div>
      <span className="tabular w-9 shrink-0 text-right text-xs text-foreground">{pct}%</span>
    </div>
  );
}

function StatusCell({ row }: { row: AnalysisRow }) {
  if (row.status === "success") {
    return <span className="text-xs text-affirmed">Berhasil</span>;
  }
  if (row.status === "skipped") {
    return <span className="text-xs text-muted-foreground">Dilewati</span>;
  }
  const label = <span className="text-xs font-medium text-wine-700">Gagal</span>;
  if (!row.error_message) return label;
  return (
    <TooltipProvider delayDuration={150}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="cursor-help underline decoration-dotted underline-offset-2">
            {label}
          </span>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-[240px] text-xs">
          {row.error_message}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

function computeConsensus(rows: AnalysisRow[]): {
  label: string;
  count: number;
  total: number;
} | null {
  const successful = rows.filter((r) => r.status === "success" && r.predicted_class);
  if (successful.length === 0) return null;
  const tally = new Map<PredictedClass, number>();
  for (const r of successful) {
    const cls = r.predicted_class as PredictedClass;
    tally.set(cls, (tally.get(cls) ?? 0) + 1);
  }
  let best: PredictedClass | null = null;
  let bestCount = 0;
  for (const [cls, count] of tally) {
    if (count > bestCount) {
      best = cls;
      bestCount = count;
    }
  }
  if (best === null) return null;
  return { label: CLASS_LABEL[best], count: bestCount, total: successful.length };
}

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

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
              <th className="py-1.5 pr-3">Arsitektur</th>
              <th className="py-1.5 pr-3">Prediksi</th>
              <th className="py-1.5 pr-3">Keyakinan</th>
              <th className="py-1.5">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-border/50 last:border-0">
                <td className="py-2 pr-3 align-middle font-medium text-foreground">
                  {row.architecture}
                </td>
                <td className="py-2 pr-3 align-middle">
                  {row.predicted_class ? (
                    <PredictionChip value={row.predicted_class} />
                  ) : (
                    <span className="text-xs text-muted-foreground">-</span>
                  )}
                </td>
                <td className="py-2 pr-3 align-middle">
                  <ConfidenceBar value={row.confidence_score} />
                </td>
                <td className="py-2 align-middle">
                  <StatusCell row={row} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

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
