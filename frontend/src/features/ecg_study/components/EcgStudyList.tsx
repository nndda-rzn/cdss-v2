import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ArrowUpRight, ScanLine } from "lucide-react";
import Zoom from "react-medium-image-zoom";
import "react-medium-image-zoom/dist/styles.css";

import { AuthedImage } from "@/components/ui/authed-image";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { QualityBadge } from "@/components/ui/quality-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";

import { ecgKeys, fetchEcgStudies } from "../api";

export function EcgStudyList({ encounterId }: { encounterId: string }) {
  const t = useI18nStore((s) => s.t);
  const { data, isLoading } = useQuery({
    queryKey: ecgKeys.list(encounterId),
    queryFn: () => fetchEcgStudies(encounterId),
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} variant="ecg" className="h-40 w-full" />
        ))}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="Belum ada studi EKG di kunjungan ini"
        description="Unggah berkas EKG (JPEG/PNG, maks 10 MB) untuk mulai analisis kualitas."
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {data.map((s) => (
        <Card key={s.id} className="overflow-hidden">
          <div className="relative bg-charcoal-50">
            <Zoom>
              <AuthedImage
                path={s.image_original_path}
                alt={`Studi EKG ${s.study_uid}`}
                className="h-40 w-full object-cover"
              />
            </Zoom>
            <div className="absolute right-2 top-2">
              <QualityBadge
                status={s.image_quality_status}
                score={s.image_quality_score}
                metrics={s.image_quality_metrics_json}
              />
            </div>
          </div>
          <div className="space-y-1 p-3 text-sm">
            <div className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
              <ScanLine className="h-3.5 w-3.5" aria-hidden="true" />
              <span>Study UID</span>
            </div>
            <div className="tabular truncate font-mono text-xs text-foreground">{s.study_uid}</div>
            <div className="tabular text-xs text-muted-foreground">
              {s.created_at.slice(0, 16).replace("T", " ")}
            </div>
            <Link
              to={`/encounters/${encounterId}/ecg-studies/${s.id}/analyses`}
              className="inline-flex items-center gap-1 pt-2 text-xs font-medium text-primary hover:underline"
            >
              {t("Lihat Analisis AI", "View AI Analysis")}
              <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
            </Link>
          </div>
        </Card>
      ))}
    </div>
  );
}
