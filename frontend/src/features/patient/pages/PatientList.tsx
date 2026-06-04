import { useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { useHotkeys } from "react-hotkeys-hook";
import { Info, Search, UserPlus } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { RoleGate } from "@/features/auth/components/RoleGate";
import { useI18nStore } from "@/lib/i18n/store";

import { fetchPatients, patientKeys } from "../api";
import { AdminModeBanner } from "../components/AdminModeBanner";

export function PatientList() {
  const t = useI18nStore((s) => s.t);
  const [searchParams] = useSearchParams();
  const action = searchParams.get("action");

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
        <h1 className="text-xl font-semibold">{t("Pasien", "Patients")}</h1>
        <RoleGate allow={["clinician", "nurse"]}>
          <Button asChild className="cursor-pointer">
            <Link to="/patients/new">
              <UserPlus className="mr-1.5 h-4 w-4" aria-hidden="true" />
              {t("Pasien Baru", "New Patient")}
            </Link>
          </Button>
        </RoleGate>
      </div>

      <AdminModeBanner />

      {action === "new-encounter" && (
        <Alert className="bg-affirmed-soft border-primary/20 text-primary">
          <Info className="h-4 w-4 text-primary" />
          <AlertTitle>{t("Buat Kunjungan Baru", "Create New Encounter")}</AlertTitle>
          <AlertDescription>
            {t(
              "Cari dan pilih pasien dari daftar di bawah untuk membuat kunjungan baru.",
              "Search and select a patient from the list below to create a new encounter.",
            )}
          </AlertDescription>
        </Alert>
      )}

      {action === "upload-ecg" && (
        <Alert className="bg-affirmed-soft border-primary/20 text-primary">
          <Info className="h-4 w-4 text-primary" />
          <AlertTitle>{t("Unggah EKG", "Upload ECG")}</AlertTitle>
          <AlertDescription>
            {t(
              "Cari dan pilih pasien dari daftar di bawah untuk mengunggah berkas EKG.",
              "Search and select a patient from the list below to upload an ECG file.",
            )}
          </AlertDescription>
        </Alert>
      )}

      <div className="relative max-w-sm">
        <Search
          className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden="true"
        />
        <Input
          ref={searchRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t("Cari MRN, nama, atau NIK...", "Search MRN, name, or NIK...")}
          aria-label={t("Cari pasien", "Search patients")}
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
          {error instanceof Error ? error.message : t("Gagal memuat", "Failed to load")}
        </p>
      )}

      {data && data.total === 0 && (
        <EmptyState
          title={t("Belum ada pasien terdaftar", "No registered patients yet")}
          description={t(
            "Daftarkan pasien pertama untuk mulai mencatat kunjungan dan studi EKG.",
            "Register the first patient to start recording encounters and ECG studies.",
          )}
          action={
            <RoleGate allow={["clinician", "nurse"]}>
              <Button asChild size="sm" className="cursor-pointer">
                <Link to="/patients/new">
                  <UserPlus className="mr-1.5 h-4 w-4" aria-hidden="true" />
                  {t("Daftarkan pasien pertama", "Register first patient")}
                </Link>
              </Button>
            </RoleGate>
          }
        />
      )}

      {data && data.total > 0 && items.length === 0 && (
        <p className="text-sm text-muted-foreground">
          {t("Tidak ada pasien yang cocok dengan", "No patients match")} &ldquo;{query}&rdquo;.
        </p>
      )}

      {items.length > 0 && (
        <table className="w-full text-sm" aria-label="Daftar Pasien">
          <caption className="sr-only">Daftar pasien yang terdaftar di fasilitas</caption>
          <thead>
            <tr className="border-b border-border-strong text-left">
              <th className="py-2 font-medium text-muted-foreground">{t("MRN", "MRN")}</th>
              <th className="py-2 font-medium text-muted-foreground">{t("Nama", "Name")}</th>
              <th className="py-2 font-medium text-muted-foreground">{t("Tgl Lahir", "DOB")}</th>
              <th className="py-2 font-medium text-muted-foreground">
                {t("Jenis Kelamin", "Gender")}
              </th>
              <th className="py-2 font-medium text-muted-foreground">{t("NIK", "NIK")}</th>
              <th className="py-2"></th>
            </tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.id} className="border-b hover:bg-sunken">
                <td className="tabular py-2">{p.mrn}</td>
                <td className="py-2">{p.name_masked}</td>
                <td className="tabular py-2">{p.dob}</td>
                <td className="py-2">
                  {p.gender === "male" ? t("Laki-laki", "Male") : t("Perempuan", "Female")}
                </td>
                <td className="tabular py-2">{p.nik_last4 ?? "-"}</td>
                <td className="py-2">
                  <Link to={`/patients/${p.id}`} className="text-primary hover:underline">
                    {t("Detail", "Detail")}
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
