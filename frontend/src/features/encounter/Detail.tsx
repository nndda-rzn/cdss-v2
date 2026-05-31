import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ContextForm } from "@/features/clinical_context/ContextForm";
import { closeEncounter, encounterKeys, fetchEncounter } from "./api";

export function Detail() {
  const { id = "" } = useParams();
  const qc = useQueryClient();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: encounterKeys.detail(id),
    queryFn: () => fetchEncounter(id),
    enabled: !!id,
  });

  const closeMutation = useMutation({
    mutationFn: () => closeEncounter(Number(id)),
    onSuccess: () => qc.invalidateQueries({ queryKey: encounterKeys.detail(id) }),
  });

  if (isLoading) return <Skeleton className="h-48 w-full max-w-lg" />;
  if (isError) {
    return (
      <p role="alert" className="text-sm text-destructive">
        {error instanceof Error ? error.message : "Gagal memuat"}
      </p>
    );
  }
  if (!data) return null;

  return (
    <div className="max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Detail Kunjungan</h1>
        {data.status === "open" && (
          <Button
            variant="outline"
            disabled={closeMutation.isPending}
            onClick={() => closeMutation.mutate()}
          >
            Tutup Kunjungan
          </Button>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Kunjungan #{data.id}
            <Badge variant={data.status === "open" ? "default" : "secondary"}>
              {data.status === "open" ? "Terbuka" : "Tertutup"}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm">
          <div className="flex justify-between border-b py-1.5">
            <span className="text-muted-foreground">Tipe</span>
            <span>{data.encounter_type === "igd" ? "IGD" : "Rawat Jalan"}</span>
          </div>
          <div className="flex justify-between border-b py-1.5">
            <span className="text-muted-foreground">Keluhan Utama</span>
            <span>{data.chief_complaint ?? "-"}</span>
          </div>
          <div className="flex justify-between border-b py-1.5">
            <span className="text-muted-foreground">Mulai</span>
            <span>{data.started_at}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Konteks Klinis</CardTitle>
        </CardHeader>
        <CardContent>
          <ContextForm encounterId={String(data.id)} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Tanda Vital</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Form tanda vital (Sprint 2A — S6).
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Studi EKG</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Upload EKG akan diaktifkan di Sprint 2B.
        </CardContent>
      </Card>

      <Link to={`/patients/${data.patient_id}`} className="text-sm text-primary underline">
        Kembali ke pasien
      </Link>
    </div>
  );
}
