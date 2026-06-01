import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { contextKeys, fetchContext, saveContext } from "../api";

const _SYMPTOMS = [
  { key: "symptom_chest_pain", label: "Nyeri dada" },
  { key: "symptom_dyspnea", label: "Sesak napas" },
  { key: "symptom_palpitation", label: "Palpitasi" },
  { key: "symptom_syncope", label: "Sinkop" },
] as const;

type SymptomKey = (typeof _SYMPTOMS)[number]["key"];

export function ContextForm({ encounterId }: { encounterId: string }) {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: contextKeys.detail(encounterId),
    queryFn: () => fetchContext(encounterId),
  });

  const [symptoms, setSymptoms] = useState<Record<SymptomKey, boolean>>({
    symptom_chest_pain: false,
    symptom_dyspnea: false,
    symptom_palpitation: false,
    symptom_syncope: false,
  });
  const [painOnset, setPainOnset] = useState("");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      saveContext(encounterId, {
        ...symptoms,
        pain_onset_minutes: painOnset ? Number(painOnset) : undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: contextKeys.detail(encounterId) }),
    onError: (err) => setError(err instanceof Error ? err.message : "Gagal"),
  });

  if (isLoading) return <p className="text-sm">Memuat...</p>;

  if (data) {
    return (
      <ul className="space-y-1 text-sm">
        {_SYMPTOMS.map((s) => (
          <li key={s.key} className="flex justify-between border-b py-1.5">
            <span>{s.label}</span>
            <span>{data[s.key] ? "Ya" : "Tidak"}</span>
          </li>
        ))}
        {data.pain_onset_minutes != null && (
          <li className="flex justify-between border-b py-1.5">
            <span>Onset nyeri (menit)</span>
            <span>{data.pain_onset_minutes}</span>
          </li>
        )}
      </ul>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2">
        {_SYMPTOMS.map((s) => {
          const isActive = symptoms[s.key];
          return (
            <button
              key={s.key}
              type="button"
              onClick={() => setSymptoms((prev) => ({ ...prev, [s.key]: !isActive }))}
              className={cn(
                "rounded-full px-3 py-1.5 text-sm font-medium transition-colors border text-center cursor-pointer",
                isActive
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-sunken text-muted-foreground border-border hover:border-border-strong",
              )}
            >
              {s.label}
            </button>
          );
        })}
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm font-medium whitespace-nowrap" htmlFor="pain-onset">
          Onset nyeri
        </label>
        <div className="flex items-center gap-2">
          <Input
            id="pain-onset"
            inputMode="numeric"
            value={painOnset}
            onChange={(e) => setPainOnset(e.target.value)}
            className="w-20 h-9"
          />
          <span className="text-sm text-muted-foreground">menit</span>
        </div>
      </div>
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      <Button
        size="sm"
        disabled={mutation.isPending}
        onClick={() => mutation.mutate()}
        className="cursor-pointer"
      >
        Simpan Konteks
      </Button>
    </div>
  );
}
