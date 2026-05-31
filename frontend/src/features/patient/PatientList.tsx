import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchPatients, patientKeys } from "./api";

export function PatientList() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: patientKeys.list({}),
    queryFn: () => fetchPatients(),
  });

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Pasien</h1>
        <Button asChild>
          <Link to="/patients/new">+ Pasien Baru</Link>
        </Button>
      </div>

      {isLoading && (
        <div className="space-y-2">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-8 w-full" />
        </div>
      )}

      {isError && (
        <p role="alert" className="text-sm text-destructive">
          {error instanceof Error ? error.message : "Gagal memuat"}
        </p>
      )}

      {data && data.total === 0 && (
        <p className="text-sm text-muted-foreground">
          Belum ada pasien terdaftar. Klik + Pasien Baru untuk memulai.
        </p>
      )}

      {data && data.total > 0 && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-2">MRN</th>
              <th className="py-2">Nama</th>
              <th className="py-2">Tgl Lahir</th>
              <th className="py-2">Jenis Kelamin</th>
              <th className="py-2">NIK</th>
              <th className="py-2"></th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((p) => (
              <tr key={p.id} className="border-b">
                <td className="py-2">{p.mrn}</td>
                <td className="py-2">{p.name_masked}</td>
                <td className="py-2">{p.dob}</td>
                <td className="py-2">{p.gender === "male" ? "Laki-laki" : "Perempuan"}</td>
                <td className="py-2">{p.nik_last4 ?? "-"}</td>
                <td className="py-2">
                  <Link to={`/patients/${p.id}`} className="text-primary underline">
                    Detail
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
