import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface Props {
  data: Record<string, number>;
  loading?: boolean;
}

const COLORS: Record<string, string> = {
  normal: "hsl(142, 76%, 36%)",
  mi: "hsl(0, 84%, 60%)",
  abnormal: "hsl(38, 92%, 50%)",
};

const LABELS: Record<string, { id: string; en: string }> = {
  normal: { id: "Normal", en: "Normal" },
  mi: { id: "MI", en: "MI" },
  abnormal: { id: "Abnormal", en: "Abnormal" },
};

export function DiagnosisDistributionChart({ data, loading }: Props) {
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

  const total = Object.values(data).reduce((a, b) => a + b, 0);
  const chartData = Object.entries(data).map(([key, value]) => ({
    name: LABELS[key]?.id ?? key,
    value,
    color: COLORS[key] ?? "hsl(var(--muted-foreground))",
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Distribusi Diagnosis AI", "AI Diagnosis Distribution")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          {t(`Total: ${total} analisis`, `Total: ${total} analyses`)}
        </p>
      </CardContent>
    </Card>
  );
}
