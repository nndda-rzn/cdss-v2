/**
 * AI-analysis presentation constants + consensus calculation.
 * Pure (no React) so the consensus logic is independently testable.
 */
import type { AnalysisRow, ExplanationStatus, PredictedClass } from "./types";

export const CLASS_LABEL: Record<PredictedClass, string> = {
  normal: "Normal",
  mi: "Infark Miokard (MI)",
  homi: "Riwayat MI",
  abnormal: "Aritmia/Abnormal",
};

export const CLASS_CHIP: Record<PredictedClass, string> = {
  normal: "bg-affirmed-soft text-primary",
  abnormal: "bg-caution-soft text-amber-700",
  mi: "bg-negative-soft text-wine-700",
  homi: "bg-negative-soft text-wine-700 ring-1 ring-inset ring-wine-700/30",
};

export interface Consensus {
  label: string;
  count: number;
  total: number;
}

export interface ConsensusDetail extends Consensus {
  /** The dominant predicted class (enum), for tone/colour selection. */
  dominantClass: PredictedClass;
  /** Mean confidence across successful analyses of the dominant class (0..1). */
  avgConfidence: number;
}

/** Richer consensus: dominant class enum + mean confidence of that class. */
export function computeConsensusDetail(rows: AnalysisRow[]): ConsensusDetail | null {
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

  const ofClass = successful.filter((r) => r.predicted_class === best);
  const avg = ofClass.reduce((sum, r) => sum + (r.confidence_score ?? 0), 0) / ofClass.length;

  return {
    label: CLASS_LABEL[best],
    count: bestCount,
    total: successful.length,
    dominantClass: best,
    avgConfidence: avg,
  };
}

// ---------------------------------------------------------------------------
// HiResCAM explanation-status labels + chip colours
// ---------------------------------------------------------------------------

export const STATUS_LABEL: Record<ExplanationStatus, string> = {
  good: "Baik",
  diffuse: "Menyebar",
  "off-target": "Tidak Fokus",
  "low-confidence": "Keyakinan Rendah",
  "need-review": "Perlu Tinjauan",
};

export const STATUS_LABEL_EN: Record<ExplanationStatus, string> = {
  good: "Good",
  diffuse: "Diffuse",
  "off-target": "Off-Target",
  "low-confidence": "Low Confidence",
  "need-review": "Need Review",
};

export const STATUS_CHIP: Record<ExplanationStatus, string> = {
  good: "bg-affirmed-soft text-primary",
  diffuse: "bg-caution-soft text-amber-700",
  "off-target": "bg-negative-soft text-wine-700",
  "low-confidence": "bg-caution-soft text-amber-700",
  "need-review": "bg-negative-soft text-wine-700",
};
