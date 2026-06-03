// frontend/src/features/tuning/components/ActiveConfigForm.tsx
import { useI18nStore } from "@/lib/i18n/store";
import type { ProductionConfig } from "../types";

interface ActiveConfigFormProps {
  form: Partial<ProductionConfig>;
  onChange: (updated: Partial<ProductionConfig>) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export function ActiveConfigForm({ form, onChange, onSubmit }: ActiveConfigFormProps) {
  const t = useI18nStore((s) => s.t);

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* ROI Crop Section */}
        <div className="space-y-2 border p-3 rounded bg-slate-50/50 dark:bg-slate-900/50">
          <div className="flex items-center gap-2 font-medium">
            <input
              type="checkbox"
              id="use_roi_crop"
              checked={form.use_roi_crop ?? false}
              onChange={(e) => onChange({ ...form, use_roi_crop: e.target.checked })}
              className="rounded text-primary focus:ring-primary h-4 w-4"
            />
            <label htmlFor="use_roi_crop">{t("Gunakan ROI Crop", "Use ROI Crop")}</label>
          </div>
          {form.use_roi_crop && (
            <div className="grid grid-cols-2 gap-2 text-xs pt-1">
              <label className="flex flex-col gap-1">
                <span>X1 (Min 0.0)</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={form.roi_x1 ?? 0}
                  onChange={(e) => onChange({ ...form, roi_x1: parseFloat(e.target.value) })}
                  className="p-1 border rounded"
                />
              </label>
              <label className="flex flex-col gap-1">
                <span>Y1 (Min 0.0)</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={form.roi_y1 ?? 0}
                  onChange={(e) => onChange({ ...form, roi_y1: parseFloat(e.target.value) })}
                  className="p-1 border rounded"
                />
              </label>
              <label className="flex flex-col gap-1">
                <span>X2 (Max 1.0)</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={form.roi_x2 ?? 0}
                  onChange={(e) => onChange({ ...form, roi_x2: parseFloat(e.target.value) })}
                  className="p-1 border rounded"
                />
              </label>
              <label className="flex flex-col gap-1">
                <span>Y2 (Max 1.0)</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={form.roi_y2 ?? 0}
                  onChange={(e) => onChange({ ...form, roi_y2: parseFloat(e.target.value) })}
                  className="p-1 border rounded"
                />
              </label>
            </div>
          )}
        </div>

        {/* Signal Masking Section */}
        <div className="space-y-2 border p-3 rounded bg-slate-50/50 dark:bg-slate-900/50">
          <div className="flex items-center gap-2 font-medium">
            <input
              type="checkbox"
              id="use_signal_mask"
              checked={form.use_signal_mask ?? false}
              onChange={(e) => onChange({ ...form, use_signal_mask: e.target.checked })}
              className="rounded text-primary focus:ring-primary h-4 w-4"
            />
            <label htmlFor="use_signal_mask">{t("Signal Masking", "Signal Masking")}</label>
          </div>
          {form.use_signal_mask && (
            <div className="grid grid-cols-2 gap-2 text-xs pt-1">
              <label className="flex flex-col gap-1 col-span-2">
                <span>{t("Kekuatan Mask (0..1)", "Mask Strength (0..1)")}</span>
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={form.signal_mask_strength ?? 0}
                  onChange={(e) =>
                    onChange({ ...form, signal_mask_strength: parseFloat(e.target.value) })
                  }
                  className="p-1 border rounded"
                />
              </label>
              <label className="flex flex-col gap-1 col-span-2">
                <span>{t("Blur Radius (px)", "Blur Radius (px)")}</span>
                <input
                  type="number"
                  min="0"
                  max="20"
                  value={form.signal_mask_blur_radius ?? 0}
                  onChange={(e) =>
                    onChange({ ...form, signal_mask_blur_radius: parseInt(e.target.value) })
                  }
                  className="p-1 border rounded"
                />
              </label>
            </div>
          )}
        </div>

        {/* Basic CAM params */}
        <div className="space-y-2 border p-3 rounded bg-slate-50/50 dark:bg-slate-900/50 grid grid-cols-2 gap-2 text-xs">
          <label className="flex flex-col gap-1">
            <span>{t("Layer Target", "Target Layer")}</span>
            <select
              value={form.target_layer_name ?? "last_conv"}
              onChange={(e) => onChange({ ...form, target_layer_name: e.target.value })}
              className="p-1 border rounded h-7 bg-white dark:bg-black"
            >
              <option value="last_conv">last_conv</option>
              <option value="second_last_conv">second_last_conv</option>
              <option value="third_last_conv">third_last_conv</option>
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span>{t("Input Size", "Input Size")}</span>
            <select
              value={form.input_size ?? 1600}
              onChange={(e) => onChange({ ...form, input_size: parseInt(e.target.value) })}
              className="p-1 border rounded h-7 bg-white dark:bg-black"
            >
              <option value="640">640</option>
              <option value="1600">1600</option>
              <option value="2048">2048</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 col-span-2">
            <span>Colormap</span>
            <select
              value={form.colormap ?? "inferno"}
              onChange={(e) => onChange({ ...form, colormap: e.target.value })}
              className="p-1 border rounded h-7 bg-white dark:bg-black"
            >
              <option value="inferno">inferno</option>
              <option value="jet">jet</option>
              <option value="turbo">turbo</option>
              <option value="viridis">viridis</option>
            </select>
          </label>
        </div>
      </div>
    </form>
  );
}
