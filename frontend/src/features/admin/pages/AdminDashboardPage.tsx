import { useQuery } from "@tanstack/react-query";
import { Building2, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import { fetchUsers, fetchFacilities, adminKeys } from "../api";

export function AdminDashboardPage() {
  const t = useI18nStore((s) => s.t);

  const { data: users, isLoading: loadingUsers } = useQuery({
    queryKey: adminKeys.users,
    queryFn: fetchUsers,
  });

  const { data: facilities, isLoading: loadingFacilities } = useQuery({
    queryKey: adminKeys.facilities,
    queryFn: fetchFacilities,
  });

  const totalUsers = users?.items.length ?? 0;
  const activeUsers = users?.items.filter((u) => u.is_active).length ?? 0;
  const totalFacilities = facilities?.items.length ?? 0;

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          {t("Admin Dashboard", "Admin Dashboard")}
        </h1>
        <p className="text-sm text-muted-foreground">
          {t("Kelola pengguna dan fasilitas sistem.", "Manage system users and facilities.")}
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              {t("Total Pengguna", "Total Users")}
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingUsers ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">
                {activeUsers} / {totalUsers}
              </div>
            )}
            <p className="text-xs text-muted-foreground">{t("aktif / total", "active / total")}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              {t("Total Fasilitas", "Total Facilities")}
            </CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingFacilities ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{totalFacilities}</div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="flex gap-3">
        <Button asChild>
          <Link to="/admin/users">
            <Users className="mr-1.5 h-4 w-4" />
            {t("Kelola Pengguna", "Manage Users")}
          </Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/admin/facilities">
            <Building2 className="mr-1.5 h-4 w-4" />
            {t("Kelola Fasilitas", "Manage Facilities")}
          </Link>
        </Button>
      </div>
    </div>
  );
}
