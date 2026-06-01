import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import { ExplanationStatusBadge } from "./ExplanationStatusBadge";
import { CLASS_CHIP, CLASS_LABEL } from "../labels";
import type { AnalysisRow, HiResCAMRow, PredictedClass } from "../types";

const CLASS_ORDER: PredictedClass[] = ["normal", "mi", "homi", "abnormal"];

function Chip({ value }: { value: PredictedClass }) {
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
      <div className="h-2 w-full overflow-hidden rounded-full bg-sunken">
        <div className="h-full rounded-full bg-petrol-600" style={{ width: `${pct}%` }} />
      </div>
      <span className="tabular w-9 shrink-0 text-right text-xs text-foreground">{pct}%</span>
    </div>
  );
}

function ProbCell({ value }: { value: number | undefined }) {
  if (value === undefined) return <span className="text-xs text-muted-foreground">-</span>;
  return <span className="tabular text-xs text-foreground">{Math.round(value * 100)}%</span>;
}

function StatusCell({ row, t }: { row: AnalysisRow; t: (id: string, en: string) => string }) {
  if (row.status === "success") {
    return <span className="text-xs text-affirmed">{t("Berhasil", "Success")}</span>;
  }
  if (row.status === "skipped") {
    return <span className="text-xs text-muted-foreground">{t("Dilewati", "Skipped")}</span>;
  }
  const label = <span className="text-xs font-medium text-wine-700">{t("Gagal", "Failed")}</span>;
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

/** Full-width comparison table for the analysis detail page. */
export function AnalysisDetailTable({
  rows,
  hirescam,
  describedById,
}: {
  rows: AnalysisRow[];
  hirescam?: HiResCAMRow[];
  describedById?: string;
}) {
  const t = useI18nStore((s) => s.t);

  return (
    <table className="w-full text-left text-sm" aria-describedby={describedById}>
      <caption className="sr-only">
        {t(
          "Perbandingan prediksi lima model YOLO untuk studi EKG ini.",
          "Comparison of five YOLO model predictions for this ECG study.",
        )}
      </caption>
      <thead>
        <tr className="border-b border-border text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
          <th className="py-2 pr-3">{t("Arsitektur", "Architecture")}</th>
          <th className="py-2 pr-3">{t("Prediksi", "Prediction")}</th>
          <th className="py-2 pr-3">{t("Keyakinan", "Confidence")}</th>
          <th className="py-2 pr-3">{t("Waktu", "Time")}</th>
          <th className="py-2 pr-3">{t("Status", "Status")}</th>
          <th className="py-2 pr-3">{t("Status Penjelasan", "Explanation")}</th>
          {CLASS_ORDER.map((c) => (
            <th key={c} className="py-2 pr-3 text-right">
              {CLASS_LABEL[c].split(" ")[0]}
            </th>
          ))}
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
                <Chip value={row.predicted_class} />
              ) : (
                <span className="text-xs text-muted-foreground">-</span>
              )}
            </td>
            <td className="min-w-[140px] py-2 pr-3 align-middle">
              <ConfidenceBar value={row.confidence_score} />
            </td>
            <td className="tabular py-2 pr-3 align-middle text-xs text-muted-foreground">
              {row.inference_time_ms !== null ? `${row.inference_time_ms} ms` : "-"}
            </td>
            <td className="py-2 pr-3 align-middle">
              <StatusCell row={row} t={t} />
            </td>
            <td className="py-2 pr-3 align-middle">
              {hirescam ? (
                (() => {
                  const hc = hirescam.find((h) => h.ai_analysis_id === row.id);
                  return hc ? (
                    <ExplanationStatusBadge status={hc.explanation_status} />
                  ) : (
                    <span className="text-xs text-muted-foreground">-</span>
                  );
                })()
              ) : (
                <span className="text-xs text-muted-foreground">-</span>
              )}
            </td>
            {CLASS_ORDER.map((c) => (
              <td key={c} className="py-2 pr-3 text-right align-middle">
                <ProbCell value={row.probability_json[c]} />
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
