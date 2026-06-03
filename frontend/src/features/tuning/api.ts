// frontend/src/features/tuning/api.ts
import { apiFetch } from "@/lib/api/client";
import type { ProductionConfig, TuningConfig, TuningMetadata } from "./types";

export const tuningKeys = {
  all: ["tuning"] as const,
  grid: () => [...tuningKeys.all, "grid"] as const,
  config: (index: number) => [...tuningKeys.all, "config", index] as const,
  active: () => [...tuningKeys.all, "active"] as const,
};

export async function fetchTuningGrid(): Promise<TuningConfig[]> {
  const resp = await apiFetch("/api/tuning/grid");
  if (!resp.ok) throw new Error("Failed to fetch tuning grid");
  const data = await resp.json();
  return data.items;
}

export async function fetchTuningConfig(index: number): Promise<TuningMetadata> {
  const resp = await apiFetch(`/api/tuning/grid/${index}`);
  if (!resp.ok) throw new Error("Failed to fetch config");
  return resp.json();
}

export function tuningImageUrl(configIndex: number, filename: string): string {
  return `/api/tuning/grid/${configIndex}/images/${filename}`;
}

export async function fetchActiveConfig(): Promise<ProductionConfig> {
  const resp = await apiFetch("/api/tuning/active");
  if (!resp.ok) throw new Error("Failed to fetch active config");
  return resp.json();
}

export async function saveActiveConfig(
  config: Partial<ProductionConfig>,
): Promise<ProductionConfig> {
  const resp = await apiFetch("/api/tuning/active", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(config),
  });
  if (!resp.ok) throw new Error("Failed to update active config");
  const data = await resp.json();
  return data.config;
}

export async function applyTuningConfig(configIndex: number): Promise<ProductionConfig> {
  const resp = await apiFetch(`/api/tuning/apply/${configIndex}`, {
    method: "POST",
  });
  if (!resp.ok) throw new Error("Failed to apply config");
  const data = await resp.json();
  return data.config;
}
