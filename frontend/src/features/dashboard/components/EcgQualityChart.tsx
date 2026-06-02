import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface Props {
  data: Record<string, number>;
  loading?: boolean;
}

const COLORS: Record<string, string> = {
  good: "hsl(142, 76%, 36%)",
  acceptable: "hsl(38, 92%, 50%)",
  poor: "hsl(0, 84%, 60%)",
};

const LABELS: Record<string, { id: string; en: string }> = {
  good: { id: "Baik", en: "Good" },
  acceptable: { id: "Cukup", en: "Acceptable" },
  poor: { id: "Buruk", en: "Poor" },
};

export function EcgQualityChart({ data, loading }: Props) {
  const t = useI18nStore((s) => s.t);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  const total = Object.values(data).reduce((a, b) => a + b, 0);
  const chartData = Object.entries(data).map(([key, value]) => ({
    name: LABELS[key]?.id ?? key,
    value,
    color: COLORS[key] ?? "hsl(var(--muted-foreground))",
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Kualitas ECG", "ECG Quality")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-32">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <YAxis
                type="category"
                dataKey="name"
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                width={80}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--paper))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "6px",
                }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          {t(`Total: ${total} ECG`, `Total: ${total} ECG`)}
        </p>
      </CardContent>
    </Card>
  );
}
