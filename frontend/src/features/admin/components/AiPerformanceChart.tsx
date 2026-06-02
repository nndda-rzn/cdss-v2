import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import type { AdminAiStats } from "../types";

interface Props {
  ai: AdminAiStats;
  loading?: boolean;
}

function GaugeBar({ value, max, label }: { value: number; max: number; label: string }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{value}</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted">
        <div className="h-2 rounded-full bg-primary" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function MiniChart({ data, color }: { data: (number | null)[]; color: string }) {
  const valid = data.filter((v): v is number => v !== null);
  if (valid.length < 2) return <div className="h-16" />;
  const max = Math.max(...valid);
  const min = Math.min(...valid);
  const range = max - min || 1;
  const w = 100 / (valid.length - 1);

  const points = valid
    .map((v, i) => {
      const x = i * w;
      const y = 100 - ((v - min) / range) * 80 - 10;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg viewBox="0 0 100 100" className="h-16 w-full" preserveAspectRatio="none">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

export function AiPerformanceChart({ ai, loading }: Props) {
  const t = useI18nStore((s) => s.t);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-48" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </CardContent>
      </Card>
    );
  }

  const inferenceValues = ai.inference_trend.map((d) => d.avg_ms);
  const confidenceValues = ai.confidence_trend.map((d) => d.avg);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Performa AI", "AI Performance")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <p className="text-sm font-medium">{t("Waktu Inferensi", "Inference Time")}</p>
            <p className="text-2xl font-bold">{ai.avg_inference_ms}ms</p>
            <GaugeBar value={ai.avg_inference_ms} max={1000} label="avg" />
            <MiniChart data={inferenceValues} color="hsl(var(--primary))" />
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium">{t("Skor Kepercayaan", "Confidence Score")}</p>
            <p className="text-2xl font-bold">{(ai.avg_confidence * 100).toFixed(1)}%</p>
            <GaugeBar value={ai.avg_confidence * 100} max={100} label="avg" />
            <MiniChart data={confidenceValues} color="hsl(142, 76%, 36%)" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
