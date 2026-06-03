// frontend/src/features/tuning/components/ActiveConfigPanel.tsx
import { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import { fetchActiveConfig, saveActiveConfig, tuningKeys } from "../api";
import type { ProductionConfig } from "../types";
import { ActiveConfigForm } from "./ActiveConfigForm";

export function ActiveConfigPanel() {
  const t = useI18nStore((s) => s.t);
  const queryClient = useQueryClient();

  const { data: activeConfig, isLoading } = useQuery({
    queryKey: tuningKeys.active(),
    queryFn: fetchActiveConfig,
  });

  const [form, setForm] = useState<Partial<ProductionConfig>>({});
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (activeConfig) {
      setForm(activeConfig);
    }
  }, [activeConfig]);

  const saveMut = useMutation({
    mutationFn: saveActiveConfig,
    onSuccess: (data) => {
      queryClient.setQueryData(tuningKeys.active(), data);
      setIsEditing(false);
    },
  });

  if (isLoading) {
    return <Skeleton className="h-48 w-full" />;
  }

  if (!activeConfig) return null;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    saveMut.mutate(form);
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-4">
        <CardTitle className="text-lg">
          {t("Konfigurasi HiResCAM Aktif", "Active HiResCAM Configuration")}
        </CardTitle>
        {!isEditing ? (
          <Button size="sm" onClick={() => setIsEditing(true)}>
            {t("Edit Parameter", "Edit Parameters")}
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => setIsEditing(false)}>
              {t("Batal", "Cancel")}
            </Button>
            <Button size="sm" onClick={handleSave} disabled={saveMut.isPending}>
              {saveMut.isPending ? t("Menyimpan...", "Saving...") : t("Simpan", "Save")}
            </Button>
          </div>
        )}
      </CardHeader>
      <CardContent>
        {isEditing ? (
          <ActiveConfigForm form={form} onChange={setForm} onSubmit={handleSave} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
            {/* ROI info */}
            <div>
              <div className="font-semibold mb-1 text-slate-500 dark:text-slate-400">
                {t("Region of Interest (ROI) Crop", "Region of Interest (ROI) Crop")}
              </div>
              <div>
                Status:{" "}
                <span className="font-medium">
                  {activeConfig.use_roi_crop ? t("Aktif", "Active") : t("Nonaktif", "Disabled")}
                </span>
              </div>
              {activeConfig.use_roi_crop && (
                <div className="mt-1 font-mono text-xs text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 p-1.5 rounded">
                  X: {activeConfig.roi_x1} - {activeConfig.roi_x2} <br />
                  Y: {activeConfig.roi_y1} - {activeConfig.roi_y2}
                </div>
              )}
            </div>

            {/* Signal masking info */}
            <div>
              <div className="font-semibold mb-1 text-slate-500 dark:text-slate-400">
                {t("Signal Masking", "Signal Masking")}
              </div>
              <div>
                Status:{" "}
                <span className="font-medium">
                  {activeConfig.use_signal_mask ? t("Aktif", "Active") : t("Nonaktif", "Disabled")}
                </span>
              </div>
              {activeConfig.use_signal_mask && (
                <div className="mt-1 font-mono text-xs text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 p-1.5 rounded">
                  {t("Kekuatan", "Strength")}: {activeConfig.signal_mask_strength} <br />
                  Blur: {activeConfig.signal_mask_blur_radius}px
                </div>
              )}
            </div>

            {/* Base params info */}
            <div>
              <div className="font-semibold mb-1 text-slate-500 dark:text-slate-400">
                {t("HiResCAM Parameter", "HiResCAM Parameter")}
              </div>
              <div className="grid grid-cols-2 gap-x-2 gap-y-1">
                <span className="text-slate-600 dark:text-slate-400">
                  {t("Layer Target", "Layer")}:
                </span>
                <span className="font-medium">{activeConfig.target_layer_name}</span>
                <span className="text-slate-600 dark:text-slate-400">
                  {t("Input Size", "Input Size")}:
                </span>
                <span className="font-medium">{activeConfig.input_size}px</span>
                <span className="text-slate-600 dark:text-slate-400">Colormap:</span>
                <span className="font-medium uppercase">{activeConfig.colormap}</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
