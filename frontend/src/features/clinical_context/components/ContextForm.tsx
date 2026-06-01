import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
    <div className="space-y-3">
      {_SYMPTOMS.map((s) => (
        <label key={s.key} className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={symptoms[s.key]}
            onChange={(e) => setSymptoms((prev) => ({ ...prev, [s.key]: e.target.checked }))}
          />
          {s.label}
        </label>
      ))}
      <div>
        <label className="text-sm" htmlFor="pain-onset">
          Onset nyeri (menit)
        </label>
        <Input
          id="pain-onset"
          inputMode="numeric"
          value={painOnset}
          onChange={(e) => setPainOnset(e.target.value)}
        />
      </div>
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      <Button disabled={mutation.isPending} onClick={() => mutation.mutate()}>
        Simpan Konteks
      </Button>
    </div>
  );
}
