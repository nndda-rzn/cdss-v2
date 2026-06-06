import { useQuery } from "@tanstack/react-query";
import { AuthedImage } from "@/components/ui/authed-image";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { ecgKeys, fetchEcgStudy } from "@/features/ecg_study/api";
import { useI18nStore } from "@/lib/i18n/store";
import Zoom from "react-medium-image-zoom";
import "react-medium-image-zoom/dist/styles.css";
import { fetchStudyHiResCAM, hirescamKeys } from "../api";

export function EcgStudyGrid({ encounterId, studyId }: { encounterId: string; studyId: string }) {
  const t = useI18nStore((s) => s.t);
  const study = useQuery({
    queryKey: ecgKeys.detail(encounterId, studyId),
    queryFn: () => fetchEcgStudy(encounterId, studyId),
    enabled: !!encounterId && !!studyId,
    retry: false,
  });
  const hirescam = useQuery({
    queryKey: hirescamKeys.study(encounterId, studyId),
    queryFn: () => fetchStudyHiResCAM(encounterId, studyId),
    enabled: !!encounterId && !!studyId,
    retry: false,
  });
  if (study.isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Skeleton variant="ecg" className="h-80 w-full" />
        <Skeleton variant="ecg" className="h-80 w-full" />
      </div>
    );
  }
  if (!study.data) return null;
  return (
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
  );
}
