import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import type { AdminAuditEntry } from "../types";

interface Props {
  entries: AdminAuditEntry[];
  loading?: boolean;
}

export function RecentAuditTable({ entries, loading }: Props) {
  const t = useI18nStore((s) => s.t);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-48" />
        </CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Aktivitas Terbaru", "Recent Activity")}</CardTitle>
      </CardHeader>
      <CardContent>
        {entries.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            {t("Belum ada aktivitas", "No activity yet")}
          </p>
        ) : (
          <div className="space-y-2">
            {entries.map((entry, i) => (
              <div
                key={i}
                className="flex items-center justify-between text-sm border-b pb-2 last:border-0"
              >
                <span>
                  <span className="font-medium">User #{entry.user_id ?? "?"}</span> {entry.action}{" "}
                  {entry.entity_type ?? ""}
                  {entry.entity_id ? ` #${entry.entity_id}` : ""}
                </span>
                <span className="text-xs text-muted-foreground">
                  {entry.created_at ? new Date(entry.created_at).toLocaleString("id-ID") : ""}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
