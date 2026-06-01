import { Link } from "react-router-dom";
import { ArrowUpRight, ChevronRight } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import type { RecentEncounter } from "./api";

interface RecentEncountersListProps {
  rows: RecentEncounter[] | undefined;
  loading?: boolean;
}

const TYPE_LABEL_ID: Record<RecentEncounter["encounter_type"], string> = {
  rawat_jalan: "Rawat Jalan",
  igd: "IGD",
};
const TYPE_LABEL_EN: Record<RecentEncounter["encounter_type"], string> = {
  rawat_jalan: "Outpatient",
  igd: "ER",
};

function formatRelative(iso: string, lang: "id" | "en"): string {
  const then = new Date(iso);
  const diffMs = Date.now() - then.getTime();
  const min = Math.round(diffMs / 60000);
  if (min < 1) return lang === "id" ? "baru saja" : "just now";
  if (min < 60) return lang === "id" ? `${min} menit lalu` : `${min} min ago`;
  const hr = Math.round(min / 60);
  if (hr < 24) return lang === "id" ? `${hr} jam lalu` : `${hr} h ago`;
  const day = Math.round(hr / 24);
  return lang === "id" ? `${day} hari lalu` : `${day} d ago`;
}

export function RecentEncountersList({ rows, loading }: RecentEncountersListProps) {
  const { lang, t } = useI18nStore.getState();
  // Subscribe so the component re-renders on language change.
  useI18nStore((s) => s.lang);

  if (loading) {
    return (
      <div className="flex flex-col gap-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} variant="ecg" className="h-12" />
        ))}
      </div>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <EmptyState
        title={t("Belum ada kunjungan", "No encounters yet")}
        description={t(
          "Kunjungan terbaru akan muncul di sini.",
          "Recent encounters will appear here.",
        )}
      />
    );
  }

  return (
    <ul className="flex flex-col divide-y divide-border">
      {rows.map((e) => (
        <li key={e.id}>
          <Link
            to={`/encounters/${e.id}`}
            className={cn(
              "group flex items-center gap-3 rounded-md px-2 py-3",
              "transition-colors hover:bg-sunken",
            )}
          >
            <span
              aria-hidden="true"
              className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-md",
                e.encounter_type === "igd"
                  ? "bg-negative-soft text-wine-700"
                  : "bg-affirmed-soft text-primary",
              )}
            >
              <ArrowUpRight className="h-4 w-4" />
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline justify-between gap-2">
                <span className="truncate text-sm font-medium text-foreground">
                  {t(TYPE_LABEL_ID[e.encounter_type], TYPE_LABEL_EN[e.encounter_type])}
                  {" · #"}
                  <span className="tabular">{e.id}</span>
                </span>
                <span
                  className={cn(
                    "shrink-0 rounded-sm px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide",
                    e.status === "open"
                      ? "bg-affirmed-soft text-primary"
                      : "bg-sunken text-muted-foreground",
                  )}
                >
                  {e.status === "open" ? t("Aktif", "Open") : t("Selesai", "Closed")}
                </span>
              </div>
              <div className="mt-0.5 flex items-center justify-between gap-2 text-xs text-muted-foreground">
                <span className="truncate">
                  {e.chief_complaint ?? t("Tanpa keluhan utama", "No chief complaint")}
                </span>
                <span className="tabular shrink-0">{formatRelative(e.started_at, lang)}</span>
              </div>
            </div>
            <ChevronRight
              className="h-4 w-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Link>
        </li>
      ))}
    </ul>
  );
}
