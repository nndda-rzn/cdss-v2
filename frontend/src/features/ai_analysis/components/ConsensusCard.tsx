import { CheckCircle2, TriangleAlert } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import { CLASS_CHIP, computeConsensusDetail } from "../labels";
import type { AnalysisRow } from "../types";

const LOW_AGREEMENT_RATIO = 0.6;

/** Prominent consensus summary across the model comparison. */
export function ConsensusCard({ rows, id }: { rows: AnalysisRow[]; id?: string }) {
  const t = useI18nStore((s) => s.t);
  const consensus = computeConsensusDetail(rows);

  if (!consensus) {
    return (
      <Card id={id}>
        <CardContent className="flex flex-col gap-1 py-5">
          <span className="section-label">{t("Konsensus", "Consensus")}</span>
          <p className="text-sm text-muted-foreground">
            {t(
              "Belum ada hasil yang berhasil untuk dihitung.",
              "No successful results to summarise yet.",
            )}
          </p>
        </CardContent>
      </Card>
    );
  }

  const pct = Math.round(consensus.avgConfidence * 100);
  const lowAgreement = consensus.count / consensus.total < LOW_AGREEMENT_RATIO;

  return (
    <Card id={id}>
      <CardContent className="flex flex-col gap-3 py-5">
        <span className="section-label">{t("Konsensus", "Consensus")}</span>

        <span
          className={cn(
            "inline-flex w-fit items-center rounded-md px-3 py-1 text-base font-semibold",
            CLASS_CHIP[consensus.dominantClass],
          )}
        >
          {consensus.label}
        </span>

        <div className="flex flex-col gap-1 text-sm text-muted-foreground">
          <span>
            <span className="tabular font-semibold text-foreground">{consensus.count}</span>{" "}
            {t("dari", "of")}{" "}
            <span className="tabular font-semibold text-foreground">{consensus.total}</span>{" "}
            {t("model setuju", "models agree")}
          </span>
          <span>
            {t("Rata-rata keyakinan", "Average confidence")}:{" "}
            <span className="tabular font-semibold text-foreground">{pct}%</span>
          </span>
        </div>

        {lowAgreement ? (
          <p className="flex items-start gap-1.5 text-xs text-amber-700">
            <TriangleAlert className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            {t(
              "Kesepakatan rendah — tinjau hasil tiap model.",
              "Low agreement — review per-model results.",
            )}
          </p>
        ) : (
          <p className="flex items-start gap-1.5 text-xs text-affirmed">
            <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            {t("Kesepakatan kuat antar model.", "Strong agreement across models.")}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
