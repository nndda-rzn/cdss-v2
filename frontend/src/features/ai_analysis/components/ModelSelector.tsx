import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useI18nStore } from "@/lib/i18n/store";

import { fetchModels, modelKeys } from "../api";

interface ModelSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

/** Radix Select dropdown for choosing an AI model before running analysis. */
export function ModelSelector({ value, onChange }: ModelSelectorProps) {
  const t = useI18nStore((s) => s.t);

  const models = useQuery({
    queryKey: modelKeys.list(),
    queryFn: fetchModels,
    retry: false,
  });

  // Auto-select first active model when data loads
  useEffect(() => {
    if (models.data && models.data.length > 0 && !value) {
      const firstActive = models.data.find((m) => m.is_active);
      if (firstActive) onChange(String(firstActive.id));
    }
  }, [models.data, value, onChange]);

  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor="model-select" className="text-xs text-muted-foreground">
        {t("Model", "Model")}
      </Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="model-select" className="w-[220px]">
          <SelectValue placeholder={t("Pilih model...", "Select model...")} />
        </SelectTrigger>
        <SelectContent>
          {models.data?.map((m) => (
            <SelectItem key={m.id} value={String(m.id)}>
              {m.model_name} {m.model_version}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
