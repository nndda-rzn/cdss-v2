import { useState } from "react";
import { Image, Layers, Split } from "lucide-react";
import Zoom from "react-medium-image-zoom";
import "react-medium-image-zoom/dist/styles.css";

import { AuthedImage } from "@/components/ui/authed-image";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import type { HiResCAMRow } from "../types";

type ViewMode = "heatmap" | "overlay" | "side-by-side";

interface Props {
  artifact: HiResCAMRow;
  originalPath: string;
  className?: string;
}

const VIEW_MODES: { mode: ViewMode; label: string; labelEn: string; icon: typeof Image }[] = [
  { mode: "heatmap", label: "Heatmap", labelEn: "Heatmap", icon: Image },
  { mode: "overlay", label: "Overlay", labelEn: "Overlay", icon: Layers },
  { mode: "side-by-side", label: "Bandingkan", labelEn: "Compare", icon: Split },
];

export function HeatmapViewer({ artifact, className }: Props) {
  const t = useI18nStore((s) => s.t);
  const [viewMode, setViewMode] = useState<ViewMode>("overlay");

  return (
    <Card className={cn("overflow-hidden", className)}>
      {/* View mode toggle */}
      <div className="flex items-center gap-1 border-b border-border px-3 py-2">
        {VIEW_MODES.map(({ mode, label, labelEn, icon: Icon }) => (
          <Button
            key={mode}
            variant={viewMode === mode ? "default" : "ghost"}
            size="sm"
            onClick={() => setViewMode(mode)}
            className="cursor-pointer"
          >
            <Icon className="mr-1.5 h-3.5 w-3.5" aria-hidden="true" />
            {t(label, labelEn)}
          </Button>
        ))}
      </div>

      {/* Image display */}
      <div className="relative bg-charcoal-50">
        <Zoom>
          {viewMode === "heatmap" && (
            <AuthedImage
              path={`api/heatmaps/${artifact.heatmap_path}`}
              alt={t("Heatmap HiResCAM", "HiResCAM Heatmap")}
              className="max-h-[600px] w-full object-contain"
            />
          )}
          {viewMode === "overlay" && (
            <AuthedImage
              path={`api/heatmaps/${artifact.overlay_path}`}
              alt={t("Overlay Heatmap", "Heatmap Overlay")}
              className="max-h-[600px] w-full object-contain"
            />
          )}
          {viewMode === "side-by-side" && (
            <AuthedImage
              path={`api/heatmaps/${artifact.side_by_side_path}`}
              alt={t("Perbandingan", "Side-by-side comparison")}
              className="max-h-[600px] w-full object-contain"
            />
          )}
        </Zoom>
      </div>

      {/* Focus metric */}
      <div className="px-4 py-2 text-xs text-muted-foreground">
        {t("Fokus sinyal", "Signal focus")}:{" "}
        <span className="tabular font-medium text-foreground">
          {Math.round(artifact.focus_metric * 100)}%
        </span>
      </div>
    </Card>
  );
}
