import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { RoleGate } from "@/features/auth/RoleGate";
import { fetchPatient, patientKeys } from "./api";
import { DeleteDialog } from "./DeleteDialog";

function Row({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div className="flex justify-between border-b py-1.5 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span>{value ?? "-"}</span>
    </div>
  );
}

export function PatientDetail() {
  const { id = "" } = useParams();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: patientKeys.detail(id),
    queryFn: () => fetchPatient(id),
    enabled: !!id,
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
    <div className="max-w-lg space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Detail Pasien</h1>
        <RoleGate allow={["admin"]}>
          <DeleteDialog patientId={data.id} />
        </RoleGate>
      </div>

      {data.is_pseudonymized ? (
        <Card>
          <CardHeader>
            <CardTitle>Data Ter-anonimisasi</CardTitle>
          </CardHeader>
          <CardContent>
            <Row label="Tanggal Lahir" value={data.dob} />
            <Row label="Jenis Kelamin" value={data.gender === "male" ? "Laki-laki" : "Perempuan"} />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Identitas</CardTitle>
          </CardHeader>
          <CardContent>
            <Row label="MRN" value={data.mrn} />
            <Row label="Nama" value={data.name} />
            <Row label="Tanggal Lahir" value={data.dob} />
            <Row label="Jenis Kelamin" value={data.gender === "male" ? "Laki-laki" : "Perempuan"} />
            <Row label="NIK (4 digit)" value={data.nik_last4} />
            <Row label="Telepon" value={data.phone} />
            <Row label="Alamat" value={data.address} />
          </CardContent>
        </Card>
      )}

      <Link to="/patients" className="text-sm text-primary underline">
        Kembali ke daftar
      </Link>
    </div>
  );
}
