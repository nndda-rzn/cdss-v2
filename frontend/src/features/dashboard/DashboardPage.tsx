import { useQuery } from "@tanstack/react-query";
import { Activity, ClipboardList, Sparkles, Users } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useI18nStore } from "@/lib/i18n/store";

import { dashboardKeys, fetchDashboardStats } from "./api";
import { KpiCard } from "./KpiCard";
import { QuickActions } from "./QuickActions";
import { RecentEncountersList } from "./RecentEncountersList";

/** Dashboard landing page — KPI cards + quick actions + recent encounters. */
export function DashboardPage() {
  const t = useI18nStore((s) => s.t);
  const { data, isLoading, isError, error } = useQuery({
    queryKey: dashboardKeys.stats(),
    queryFn: fetchDashboardStats,
    staleTime: 30_000,
  });

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          {t("Ringkasan aktivitas klinis hari ini.", "Summary of today's clinical activity.")}
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={t("Total Pasien", "Total Patients")}
          value={data?.total_patients ?? 0}
          icon={Users}
          tone="brand"
          loading={isLoading}
          hint={t("Terdaftar di fasilitas", "Registered at facility")}
        />
        <KpiCard
          label={t("Kunjungan Aktif", "Active Encounters")}
          value={data?.active_encounters ?? 0}
          icon={Activity}
          tone="caution"
          loading={isLoading}
          hint={t("Belum ditutup", "Not yet closed")}
        />
        <KpiCard
          label={t("Analisis AI Hari Ini", "AI Analyses Today")}
          value={data?.analyses_today ?? 0}
          icon={Sparkles}
          tone="brand"
          loading={isLoading}
          hint={t("Sejak pukul 00:00 UTC", "Since 00:00 UTC")}
        />
        <KpiCard
          label={t("Tugas Tertunda", "Pending Tasks")}
          value={data?.pending_tasks ?? 0}
          icon={ClipboardList}
          tone="negative"
          loading={isLoading}
          hint={t("Kunjungan terbuka", "Open encounters")}
        />
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
          <div>
            <CardTitle>{t("Aksi Cepat", "Quick Actions")}</CardTitle>
            <p className="text-xs text-muted-foreground">
              {t("Mulai pekerjaan klinis umum.", "Start common clinical workflows.")}
            </p>
          </div>
        </CardHeader>
        <CardContent>
          <QuickActions />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("Kunjungan Terbaru", "Recent Encounters")}</CardTitle>
          <p className="text-xs text-muted-foreground">
            {t(
              "Lima kunjungan terbaru di fasilitas Anda.",
              "Five most recent encounters at your facility.",
            )}
          </p>
        </CardHeader>
        <CardContent>
          {isError ? (
            <p role="alert" className="text-sm text-destructive">
              {error instanceof Error
                ? error.message
                : t("Gagal memuat data", "Failed to load data")}
            </p>
          ) : (
            <RecentEncountersList rows={data?.recent_encounters} loading={isLoading} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
