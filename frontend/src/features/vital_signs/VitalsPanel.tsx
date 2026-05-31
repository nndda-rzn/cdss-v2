import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Droplet, Heart, Thermometer, Wind } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

import { captureVitals, fetchVitals, vitalsKeys, type VitalRow, type VitalsInput } from "./api";

const _FIELDS = [
  { key: "bp_systolic", label: "Sistolik" },
  { key: "bp_diastolic", label: "Diastolik" },
  { key: "heart_rate", label: "Nadi" },
  { key: "respiratory_rate", label: "Napas" },
  { key: "spo2", label: "SpO2" },
  { key: "temperature", label: "Suhu" },
] as const;

type FieldKey = (typeof _FIELDS)[number]["key"];

type Status = "ok" | "caution" | "negative" | "unknown";

const TONE: Record<Status, string> = {
  ok: "border-border-strong bg-paper",
  caution: "border-amber-500/30 bg-caution-soft",
  negative: "border-wine-500/30 bg-negative-soft",
  unknown: "border-dashed border-border bg-sunken",
};

const DOT: Record<Status, string> = {
  ok: "bg-affirmed",
  caution: "bg-caution",
  negative: "bg-negative",
  unknown: "bg-charcoal-300",
};

function classify(latest: VitalRow): {
  bp: Status;
  hr: Status;
  spo2: Status;
  temp: Status;
  resp: Status;
} {
  const sys = latest.bp_systolic;
  const dia = latest.bp_diastolic;
  const bp: Status =
    sys === null || dia === null
      ? "unknown"
      : sys >= 180 || dia >= 110 || sys < 90
        ? "negative"
        : sys >= 140 || dia >= 90
          ? "caution"
          : "ok";
  const hr: Status =
    latest.heart_rate === null
      ? "unknown"
      : latest.heart_rate < 50 || latest.heart_rate > 130
        ? "negative"
        : latest.heart_rate < 60 || latest.heart_rate > 100
          ? "caution"
          : "ok";
  const spo2: Status =
    latest.spo2 === null
      ? "unknown"
      : latest.spo2 < 90
        ? "negative"
        : latest.spo2 < 95
          ? "caution"
          : "ok";
  const temp: Status =
    latest.temperature === null
      ? "unknown"
      : latest.temperature < 35 || latest.temperature >= 39
        ? "negative"
        : latest.temperature >= 38
          ? "caution"
          : "ok";
  const resp: Status =
    latest.respiratory_rate === null
      ? "unknown"
      : latest.respiratory_rate < 10 || latest.respiratory_rate > 30
        ? "negative"
        : latest.respiratory_rate > 24
          ? "caution"
          : "ok";
  return { bp, hr, spo2, temp, resp };
}

function MiniCard({
  icon: Icon,
  label,
  value,
  unit,
  status,
}: {
  icon: typeof Heart;
  label: string;
  value: string;
  unit?: string;
  status: Status;
}) {
  return (
    <div className={cn("flex flex-col gap-1 rounded-sm border px-3 py-2", TONE[status])}>
      <div className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
        <Icon className="h-3.5 w-3.5" aria-hidden="true" />
        <span>{label}</span>
        <span aria-hidden="true" className={cn("ml-auto h-1.5 w-1.5 rounded-full", DOT[status])} />
      </div>
      <div className="flex items-baseline gap-1">
        <span className="tabular text-lg font-semibold text-foreground">{value}</span>
        {unit && <span className="text-xs text-muted-foreground">{unit}</span>}
      </div>
    </div>
  );
}

export function VitalsPanel({ encounterId }: { encounterId: string }) {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: vitalsKeys.list(encounterId),
    queryFn: () => fetchVitals(encounterId),
  });

  const [values, setValues] = useState<Record<FieldKey, string>>({
    bp_systolic: "",
    bp_diastolic: "",
    heart_rate: "",
    respiratory_rate: "",
    spo2: "",
    temperature: "",
  });
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
      setValues({
        bp_systolic: "",
        bp_diastolic: "",
        heart_rate: "",
        respiratory_rate: "",
        spo2: "",
        temperature: "",
      });
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
