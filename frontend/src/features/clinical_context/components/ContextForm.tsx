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
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-2.5">
        {_SYMPTOMS.map((s) => {
          const isActive = symptoms[s.key];
          return (
            <button
              key={s.key}
              type="button"
              onClick={() => setSymptoms((prev) => ({ ...prev, [s.key]: !isActive }))}
              className={cn(
                "rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-200 border text-center cursor-pointer",
                isActive
                  ? "bg-primary text-primary-foreground border-primary shadow-sm"
                  : "bg-card text-muted-foreground border-border hover:border-primary/50 hover:bg-accent/50",
              )}
            >
              {s.label}
            </button>
          );
        })}
      </div>
      <div className="space-y-1.5">
        <label className="block text-sm font-medium text-foreground" htmlFor="pain-onset">
          Onset nyeri
        </label>
        <div className="flex items-center gap-2">
          <Input
            id="pain-onset"
            inputMode="numeric"
            value={painOnset}
            onChange={(e) => setPainOnset(e.target.value)}
            className="w-24"
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
        disabled={mutation.isPending}
        onClick={() => mutation.mutate()}
        className="w-full mt-4 cursor-pointer"
      >
        Simpan Konteks
      </Button>
    </div>
  );
}
