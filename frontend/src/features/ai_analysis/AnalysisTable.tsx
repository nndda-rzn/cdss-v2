import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

import type { AnalysisRow, PredictedClass } from "./api";
import { CLASS_CHIP, CLASS_LABEL } from "./labels";

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

/** Comparison table: one row per model with prediction, confidence, status. */
export function AnalysisTable({ rows }: { rows: AnalysisRow[] }) {
  return (
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
  );
}

AnalysisTable.displayName = "AnalysisTable";
