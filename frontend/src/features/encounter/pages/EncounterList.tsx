import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import { encounterKeys, fetchEncounters } from "../api";

export function EncounterList() {
  const t = useI18nStore((s) => s.t);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: encounterKeys.list(),
    queryFn: fetchEncounters,
  });

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">{t("Kunjungan", "Encounters")}</h1>

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

      {data && data.length === 0 && (
        <EmptyState
          title={t("Belum ada kunjungan", "No encounters yet")}
          description={t(
            "Buat kunjungan baru dari halaman detail pasien.",
            "Create a new encounter from a patient detail page.",
          )}
        />
      )}

      {data && data.length > 0 && (
        <table className="w-full text-sm" aria-label="Daftar Kunjungan">
          <caption className="sr-only">Daftar kunjungan di fasilitas</caption>
          <thead>
            <tr className="border-b border-border-strong text-left">
              <th className="py-2 font-medium text-muted-foreground">#</th>
              <th className="py-2 font-medium text-muted-foreground">{t("Tipe", "Type")}</th>
              <th className="py-2 font-medium text-muted-foreground">{t("Status", "Status")}</th>
              <th className="py-2 font-medium text-muted-foreground">
                {t("Keluhan", "Complaint")}
              </th>
              <th className="py-2 font-medium text-muted-foreground">{t("Mulai", "Started")}</th>
              <th className="py-2"></th>
            </tr>
          </thead>
          <tbody>
            {data.map((e) => (
              <tr key={e.id} className="border-b hover:bg-sunken">
                <td className="tabular py-2">{e.id}</td>
                <td className="py-2">
                  {e.encounter_type === "igd" ? t("IGD", "ER") : t("Rawat Jalan", "Outpatient")}
                </td>
                <td className="py-2">
                  <span
                    className={cn(
                      "rounded-sm px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide",
                      e.status === "open"
                        ? "bg-affirmed-soft text-primary"
                        : "bg-sunken text-muted-foreground",
                    )}
                  >
                    {e.status === "open" ? t("Aktif", "Open") : t("Selesai", "Closed")}
                  </span>
                </td>
                <td className="py-2">{e.chief_complaint ?? t("Tanpa keluhan", "No complaint")}</td>
                <td className="tabular py-2">{new Date(e.started_at).toLocaleDateString()}</td>
                <td className="py-2">
                  <Link to={`/encounters/${e.id}`} className="text-primary hover:underline">
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
