import { useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useHotkeys } from "react-hotkeys-hook";
import { Search, UserPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

import { fetchPatients, patientKeys } from "./api";

export function PatientList() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: patientKeys.list({}),
    queryFn: () => fetchPatients(),
  });

  const [query, setQuery] = useState("");
  const searchRef = useRef<HTMLInputElement>(null);

  // Ctrl/Cmd+K focuses the search input (clinical efficiency).
  useHotkeys(
    "mod+k",
    (e) => {
      e.preventDefault();
      searchRef.current?.focus();
    },
    { enableOnFormTags: true },
  );

  const items = useMemo(() => {
    if (!data) return [];
    const q = query.trim().toLowerCase();
    if (!q) return data.items;
    return data.items.filter(
      (p) =>
        p.mrn.toLowerCase().includes(q) ||
        p.name_masked.toLowerCase().includes(q) ||
        (p.nik_last4 ?? "").includes(q),
    );
  }, [data, query]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Pasien</h1>
        <Button asChild className="cursor-pointer">
          <Link to="/patients/new">
            <UserPlus className="mr-1.5 h-4 w-4" aria-hidden="true" />
            Pasien Baru
          </Link>
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search
          className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden="true"
        />
        <Input
          ref={searchRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Cari MRN, nama, atau NIK..."
          aria-label="Cari pasien"
          className="pl-8 pr-16"
        />
        <kbd className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 rounded-sm border border-border-strong bg-sunken px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
          Ctrl K
        </kbd>
      </div>

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="ecg" className="h-9 w-full" />
          ))}
        </div>
      )}

      {isError && (
        <p role="alert" className="text-sm text-destructive">
          {error instanceof Error ? error.message : "Gagal memuat"}
        </p>
      )}

      {data && data.total === 0 && (
        <EmptyState
          title="Belum ada pasien terdaftar"
          description="Daftarkan pasien pertama untuk mulai mencatat kunjungan dan studi EKG."
          action={
            <Button asChild size="sm" className="cursor-pointer">
              <Link to="/patients/new">
                <UserPlus className="mr-1.5 h-4 w-4" aria-hidden="true" />
                Daftarkan pasien pertama
              </Link>
            </Button>
          }
        />
      )}

      {data && data.total > 0 && items.length === 0 && (
        <p className="text-sm text-muted-foreground">
          Tidak ada pasien yang cocok dengan &ldquo;{query}&rdquo;.
        </p>
      )}

      {items.length > 0 && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border-strong text-left">
              <th className="py-2 font-medium text-muted-foreground">MRN</th>
              <th className="py-2 font-medium text-muted-foreground">Nama</th>
              <th className="py-2 font-medium text-muted-foreground">Tgl Lahir</th>
              <th className="py-2 font-medium text-muted-foreground">Jenis Kelamin</th>
              <th className="py-2 font-medium text-muted-foreground">NIK</th>
              <th className="py-2"></th>
            </tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.id} className="border-b hover:bg-sunken">
                <td className="tabular py-2">{p.mrn}</td>
                <td className="py-2">{p.name_masked}</td>
                <td className="tabular py-2">{p.dob}</td>
                <td className="py-2">{p.gender === "male" ? "Laki-laki" : "Perempuan"}</td>
                <td className="tabular py-2">{p.nik_last4 ?? "-"}</td>
                <td className="py-2">
                  <Link to={`/patients/${p.id}`} className="text-primary hover:underline">
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
