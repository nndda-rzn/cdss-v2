import { useQuery } from "@tanstack/react-query";
import { Building2, Cpu, Users, Activity, Heart, Zap } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useI18nStore } from "@/lib/i18n/store";
import { fetchAdminStats, adminKeys } from "../api";
import { AdminKpiCard } from "../components/AdminKpiCard";
import { AiPerformanceChart } from "../components/AiPerformanceChart";
import { RecentAuditTable } from "../components/RecentAuditTable";

const FALLBACK_AI = {
  analyses_today: 0,
  yesterday: 0,
  avg_inference_ms: 0,
  avg_confidence: 0,
  inference_trend: [],
  confidence_trend: [],
};

export function AdminDashboardPage() {
  const t = useI18nStore((s) => s.t);
  const { data, isLoading } = useQuery({
    queryKey: adminKeys.stats,
    queryFn: fetchAdminStats,
  });

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          {t("Admin Dashboard", "Admin Dashboard")}
        </h1>
        <p className="text-sm text-muted-foreground">
          {t("Pantau sistem dan kelola data.", "Monitor system and manage data.")}
        </p>
      </header>

      {/* Row 1: System Health */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <AdminKpiCard
          label={t("Total Pengguna", "Total Users")}
          value={data ? `${data.users.active} / ${data.users.total}` : 0}
          icon={Users}
          hint={t("aktif / total", "active / total")}
          loading={isLoading}
        />
        <AdminKpiCard
          label={t("Sesi Aktif", "Active Sessions")}
          value={data?.sessions.active ?? 0}
          icon={Activity}
          loading={isLoading}
        />
        <AdminKpiCard
          label={t("Model AI", "AI Model")}
          value={data?.model.name ?? "-"}
          icon={Cpu}
          hint={data?.model.version ? `v${data.model.version}` : undefined}
          loading={isLoading}
        />
      </div>

      {/* Row 2: Clinical Activity */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <AdminKpiCard
          label={t("Total Pasien", "Total Patients")}
          value={data?.patients.total ?? 0}
          icon={Users}
          loading={isLoading}
        />
        <AdminKpiCard
          label={t("Kunjungan Hari Ini", "Encounters Today")}
          value={data?.encounters.today ?? 0}
          icon={Heart}
          trend={
            data
              ? {
                  value: data.encounters.today - data.encounters.yesterday,
                  label: t("vs kemarin", "vs yesterday"),
                }
              : undefined
          }
          loading={isLoading}
        />
        <AdminKpiCard
          label={t("ECG Hari Ini", "ECG Today")}
          value={data?.ecg.today ?? 0}
          icon={Zap}
          trend={
            data
              ? {
                  value: data.ecg.today - data.ecg.yesterday,
                  label: t("vs kemarin", "vs yesterday"),
                }
              : undefined
          }
          loading={isLoading}
        />
      </div>

      {/* Row 3: AI Performance */}
      <AiPerformanceChart ai={data?.ai ?? FALLBACK_AI} loading={isLoading} />

      {/* Row 4: Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>{t("Aksi Cepat", "Quick Actions")}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button asChild>
            <Link to="/admin/users">
              <Users className="mr-1.5 h-4 w-4" />
              {t("Kelola User", "Manage Users")}
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link to="/admin/facilities">
              <Building2 className="mr-1.5 h-4 w-4" />
              {t("Kelola Fasilitas", "Manage Facilities")}
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link to="/tuning">
              <Cpu className="mr-1.5 h-4 w-4" />
              {t("Tuning AI", "AI Tuning")}
            </Link>
          </Button>
        </CardContent>
      </Card>

      {/* Row 5: Recent Activity */}
      <RecentAuditTable entries={data?.audit ?? []} loading={isLoading} />
    </div>
  );
}
