import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Droplet, Heart, Thermometer, Wind } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";

import { captureVitals, fetchVitals, vitalsKeys, type VitalsInput } from "./api";
import { MiniCard } from "./MiniCard";
import { classify } from "./ranges";

const _FIELDS = [
  { key: "bp_systolic", label: "Sistolik" },
  { key: "bp_diastolic", label: "Diastolik" },
  { key: "heart_rate", label: "Nadi" },
  { key: "respiratory_rate", label: "Napas" },
  { key: "spo2", label: "SpO2" },
  { key: "temperature", label: "Suhu" },
] as const;

type FieldKey = (typeof _FIELDS)[number]["key"];

const _EMPTY: Record<FieldKey, string> = {
  bp_systolic: "",
  bp_diastolic: "",
  heart_rate: "",
  respiratory_rate: "",
  spo2: "",
  temperature: "",
};

export function VitalsPanel({ encounterId }: { encounterId: string }) {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: vitalsKeys.list(encounterId),
    queryFn: () => fetchVitals(encounterId),
  });

  const [values, setValues] = useState<Record<FieldKey, string>>({ ..._EMPTY });
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => {
      const input: VitalsInput = {};
      for (const { key } of _FIELDS) {
        if (values[key]) input[key] = Number(values[key]);
      }
      return captureVitals(encounterId, input);
    },
    onSuccess: () => {
      setValues({ ..._EMPTY });
      setError(null);
      qc.invalidateQueries({ queryKey: vitalsKeys.list(encounterId) });
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Gagal"),
  });

  const latest = data?.[0];
  const status = latest ? classify(latest) : null;

  return (
    <div className="space-y-4">
      {latest && status ? (
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
          <MiniCard
            icon={Activity}
            label="Tekanan Darah"
            value={`${latest.bp_systolic ?? "-"}/${latest.bp_diastolic ?? "-"}`}
            unit="mmHg"
            status={status.bp}
          />
          <MiniCard
            icon={Heart}
            label="Nadi"
            value={`${latest.heart_rate ?? "-"}`}
            unit="bpm"
            status={status.hr}
          />
          <MiniCard
            icon={Droplet}
            label="SpO2"
            value={`${latest.spo2 ?? "-"}`}
            unit="%"
            status={status.spo2}
          />
          <MiniCard
            icon={Thermometer}
            label="Suhu"
            value={`${latest.temperature ?? "-"}`}
            unit="\u00B0C"
            status={status.temp}
          />
          <MiniCard
            icon={Wind}
            label="Napas"
            value={`${latest.respiratory_rate ?? "-"}`}
            unit="rpm"
            status={status.resp}
          />
        </div>
      ) : (
        <EmptyState
          title="Belum ada pengukuran"
          description="Tambahkan tanda vital untuk konteks klinis."
          hideMotif
        />
      )}

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {_FIELDS.map((f) => (
          <div key={f.key} className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground" htmlFor={f.key}>
              {f.label}
            </label>
            <Input
              id={f.key}
              inputMode="numeric"
              value={values[f.key]}
              onChange={(e) => setValues((prev) => ({ ...prev, [f.key]: e.target.value }))}
            />
          </div>
        ))}
      </div>
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      <Button
        disabled={mutation.isPending}
        onClick={() => mutation.mutate()}
        className="cursor-pointer"
      >
        {mutation.isPending ? "Menyimpan..." : "Tambah Pengukuran"}
      </Button>
    </div>
  );
}
