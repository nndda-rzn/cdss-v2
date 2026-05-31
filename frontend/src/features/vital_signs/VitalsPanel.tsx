import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { captureVitals, fetchVitals, vitalsKeys, type VitalsInput } from "./api";

const _FIELDS = [
  { key: "bp_systolic", label: "Sistolik" },
  { key: "bp_diastolic", label: "Diastolik" },
  { key: "heart_rate", label: "Nadi" },
  { key: "respiratory_rate", label: "Napas" },
  { key: "spo2", label: "SpO2" },
  { key: "temperature", label: "Suhu" },
] as const;

type FieldKey = (typeof _FIELDS)[number]["key"];

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
      qc.invalidateQueries({ queryKey: vitalsKeys.list(encounterId) });
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Gagal"),
  });

  return (
    <div className="space-y-3">
      {data && data.length > 0 && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-1">Waktu</th>
              <th className="py-1">TD</th>
              <th className="py-1">Nadi</th>
              <th className="py-1">SpO2</th>
            </tr>
          </thead>
          <tbody>
            {data.map((v) => (
              <tr key={v.id} className="border-b">
                <td className="py-1">{v.measured_at.slice(0, 16)}</td>
                <td className="py-1">
                  {v.bp_systolic ?? "-"}/{v.bp_diastolic ?? "-"}
                </td>
                <td className="py-1">{v.heart_rate ?? "-"}</td>
                <td className="py-1">{v.spo2 ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="grid grid-cols-3 gap-2">
        {_FIELDS.map((f) => (
          <div key={f.key}>
            <label className="text-xs" htmlFor={f.key}>
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
      <Button disabled={mutation.isPending} onClick={() => mutation.mutate()}>
        Tambah Pengukuran
      </Button>
    </div>
  );
}
