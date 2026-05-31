import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { addHistory, fetchHistory, historyKeys } from "./api";

const _CONDITIONS = ["MI", "DM", "HT", "CKD", "dyslipidemia", "smoker", "other"];

export function HistoryPanel({ patientId }: { patientId: string }) {
  const qc = useQueryClient();
  const [condition, setCondition] = useState("MI");
  const [note, setNote] = useState("");

  const { data } = useQuery({
    queryKey: historyKeys.list(patientId),
    queryFn: () => fetchHistory(patientId),
  });

  const mutation = useMutation({
    mutationFn: () => addHistory(patientId, condition, note || undefined),
    onSuccess: () => {
      setNote("");
      qc.invalidateQueries({ queryKey: historyKeys.list(patientId) });
    },
  });

  return (
    <div className="space-y-3">
      <ul className="space-y-1 text-sm">
        {(data ?? []).map((h) => (
          <li key={h.id} className="border-b py-1.5">
            <span className="font-medium">{h.condition_code}</span>
            {h.note ? ` — ${h.note}` : ""}
          </li>
        ))}
        {data && data.length === 0 && <li className="text-muted-foreground">Belum ada riwayat</li>}
      </ul>
      <div className="flex items-end gap-2">
        <Select value={condition} onValueChange={setCondition}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {_CONDITIONS.map((c) => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input
          aria-label="Catatan riwayat"
          placeholder="Catatan (opsional)"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <Button disabled={mutation.isPending} onClick={() => mutation.mutate()}>
          Tambah
        </Button>
      </div>
    </div>
  );
}
