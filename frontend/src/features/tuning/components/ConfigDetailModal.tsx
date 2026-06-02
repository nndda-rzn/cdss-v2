// frontend/src/features/tuning/components/ConfigDetailModal.tsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchTuningConfig, tuningImageUrl, tuningKeys } from "../api";
import type { TuningConfig } from "../types";

interface ConfigDetailModalProps {
  config: TuningConfig | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

type ViewMode = "overlay" | "heatmap" | "original";

const imageFiles: Record<ViewMode, string> = {
  overlay: "overlay.png",
  heatmap: "heatmap_colored.png",
  original: "original.png",
};

export function ConfigDetailModal({ config, open, onOpenChange }: ConfigDetailModalProps) {
  const [viewMode, setViewMode] = useState<ViewMode>("overlay");

  const { data: metadata, isLoading } = useQuery({
    queryKey: tuningKeys.config(config?.config_index ?? 0),
    queryFn: () => fetchTuningConfig(config!.config_index),
    enabled: open && config !== null,
  });

  if (!config) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Config #{config.config_index}</DialogTitle>
          <DialogDescription className="sr-only">
            Detail konfigurasi HiResCAM #{config.config_index}
          </DialogDescription>
        </DialogHeader>

        {/* View mode toggle */}
        <div className="flex gap-2">
          {(["overlay", "heatmap", "original"] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`px-3 py-1 rounded text-sm ${
                viewMode === mode ? "bg-primary text-primary-foreground" : "bg-muted"
              }`}
            >
              {mode}
            </button>
          ))}
        </div>

        {/* Image */}
        <div className="aspect-[4/3] overflow-hidden rounded-md bg-muted">
          <img
            src={tuningImageUrl(config.config_index, imageFiles[viewMode])}
            alt={`Config ${config.config_index} ${viewMode}`}
            className="w-full h-full object-contain"
          />
        </div>

        {/* Metadata */}
        {isLoading ? (
          <Skeleton className="h-20" />
        ) : (
          metadata && (
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>Input size: {metadata.input_size}</div>
              <div>Layer: {metadata.target_layer}</div>
              <div>Smooth: {metadata.smooth_sigma}</div>
              <div>Top%: {metadata.top_percent}</div>
              <div>
                Focus: {metadata.focus_metric != null ? metadata.focus_metric.toFixed(3) : "N/A"}
              </div>
              <div>
                <Badge variant="secondary">{metadata.explanation_status ?? "N/A"}</Badge>
              </div>
            </div>
          )
        )}
      </DialogContent>
    </Dialog>
  );
}
