import { ScanLine } from "lucide-react";
import Zoom from "react-medium-image-zoom";
import "react-medium-image-zoom/dist/styles.css";

import { AuthedImage } from "@/components/ui/authed-image";
import { Card } from "@/components/ui/card";
import { QualityBadge } from "@/components/ui/quality-badge";
import { useI18nStore } from "@/lib/i18n/store";

import type { EcgStudyRow } from "@/features/ecg_study/types";

/** Left column of the analysis detail page: large zoomable ECG + metadata. */
export function StudyHeaderCard({ study }: { study: EcgStudyRow }) {
  const t = useI18nStore((s) => s.t);

  return (
    <Card className="overflow-hidden">
      <div className="relative bg-charcoal-50">
        <Zoom>
          <AuthedImage
            path={study.image_original_path}
            alt={`${t("Studi EKG", "ECG study")} ${study.study_uid}`}
            className="max-h-[600px] w-full object-contain"
          />
        </Zoom>
        <div className="absolute right-2 top-2">
          <QualityBadge
            status={study.image_quality_status}
            score={study.image_quality_score}
            metrics={study.image_quality_metrics_json}
          />
        </div>
      </div>
      <div className="space-y-1 p-4 text-sm">
        <div className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
          <ScanLine className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Study UID</span>
        </div>
        <div className="tabular truncate font-mono text-xs text-foreground">{study.study_uid}</div>
        <div className="tabular text-xs text-muted-foreground">
          {t("Diakuisisi", "Acquired")}: {study.acquired_at.slice(0, 16).replace("T", " ")}
        </div>
      </div>
    </Card>
  );
}
