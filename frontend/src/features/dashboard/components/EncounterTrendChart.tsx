import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { EncounterTrendEntry } from "../types";

interface Props {
  data: EncounterTrendEntry[];
  loading?: boolean;
}

export function EncounterTrendChart({ data, loading }: Props) {
  const t = useI18nStore((s) => s.t);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-48 w-full" />
        </CardContent>
      </Card>
    );
  }

  const today = data[data.length - 1]?.count ?? 0;
  const yesterday = data[data.length - 2]?.count ?? 0;
  const diff = today - yesterday;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Tren Kunjungan (7 Hari)", "Encounter Trend (7 Days)")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="date"
                tickFormatter={(v) => new Date(v).toLocaleDateString("id-ID", { weekday: "short" })}
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
              />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--paper))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "6px",
                }}
              />
              <Area
                type="monotone"
                dataKey="count"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary) / 0.1)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          {diff >= 0 ? `↑ ${diff}` : `↓ ${Math.abs(diff)}`} {t("dari kemarin", "vs yesterday")}
        </p>
      </CardContent>
    </Card>
  );
}
