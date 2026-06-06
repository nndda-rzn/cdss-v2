import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { captureConsent, consentKeys, fetchConsents, type ConsentRow } from "../api";

const _TYPE_LABELS: Record<string, string> = {
  data_use: "Penggunaan Data",
  ai_analysis: "Analisis AI",
  research: "Penelitian",
};

function latestByType(rows: ConsentRow[]): Map<string, ConsentRow> {
  const map = new Map<string, ConsentRow>();
  for (const row of rows) {
    if (!map.has(row.consent_type)) {
      map.set(row.consent_type, row);
    }
  }
  return map;
}

export function ConsentPanel({ patientId }: { patientId: string }) {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: consentKeys.list(patientId),
    queryFn: () => fetchConsents(patientId),
  });

  const mutation = useMutation({
    mutationFn: ({ type, status }: { type: string; status: "given" | "revoked" }) =>
      captureConsent(patientId, type, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: consentKeys.list(patientId) }),
  });

  const latest = latestByType(data ?? []);
  const [revokeTarget, setRevokeTarget] = useState<string | null>(null);

  return (
    <div className="space-y-2">
      {(["data_use", "ai_analysis", "research"] as const).map((type) => {
        const current = latest.get(type);
        const given = current?.status === "given";
        return (
          <div key={type} className="flex items-center justify-between border-b py-1.5 text-sm">
            <span>{_TYPE_LABELS[type]}</span>
            <span className="flex items-center gap-2">
              <span className={given ? "text-green-600" : "text-muted-foreground"}>
                {given ? "Diberikan" : (current?.status ?? "Belum")}
              </span>
              <Button
                size="sm"
                variant="outline"
                disabled={mutation.isPending}
                onClick={() => {
                  if (given) {
                    setRevokeTarget(type);
                  } else {
                    mutation.mutate({ type, status: "given" });
                  }
                }}
              >
                {given ? "Cabut" : "Berikan"}
              </Button>
            </span>
          </div>
        );
      })}
      <ConfirmDialog
        open={revokeTarget !== null}
        onOpenChange={(open) => {
          if (!open) setRevokeTarget(null);
        }}
        title="Cabut Persetujuan?"
        description={`Apakah Anda yakin ingin mencabut persetujuan "${revokeTarget ? _TYPE_LABELS[revokeTarget] : ""}"? Tindakan ini dapat dibatalkan dengan memberikan ulang.`}
        confirmLabel="Ya, Cabut"
        cancelLabel="Batal"
        variant="destructive"
        onConfirm={() => {
          if (revokeTarget) {
            mutation.mutate({ type: revokeTarget, status: "revoked" });
            setRevokeTarget(null);
          }
        }}
      />
    </div>
  );
}
