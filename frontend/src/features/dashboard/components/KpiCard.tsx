import type { LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
  /** Optional secondary line, e.g. "Kunjungan hari ini" / "Visits today". */
  hint?: string;
  /** Tone tints the icon chip. Defaults to brand petrol. */
  tone?: "brand" | "caution" | "negative" | "neutral";
  /** Render the loading skeleton instead of the value. */
  loading?: boolean;
}

const TONE_BG: Record<NonNullable<KpiCardProps["tone"]>, string> = {
  brand: "bg-affirmed-soft text-primary",
  caution: "bg-caution-soft text-amber-700",
  negative: "bg-negative-soft text-wine-700",
  neutral: "bg-sunken text-muted-foreground",
};

/** Single SaaS-style KPI tile. Layout: small icon chip top-right, big number,
 *  label above and an optional hint below. */
export function KpiCard({ label, value, icon: Icon, hint, tone = "brand", loading }: KpiCardProps) {
  return (
    <Card className="flex flex-col gap-3 p-5">
      <div className="flex items-start justify-between gap-3">
        <span className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </span>
        <span
          aria-hidden="true"
          className={cn(
            "flex h-8 w-8 shrink-0 items-center justify-center rounded-md",
            TONE_BG[tone],
          )}
        >
          <Icon className="h-4 w-4" />
        </span>
      </div>
      {loading ? (
        <Skeleton className="h-8 w-20" />
      ) : (
        <div className="tabular text-2xl font-semibold leading-none text-foreground">{value}</div>
      )}
      {hint && <div className="text-xs text-muted-foreground">{hint}</div>}
    </Card>
  );
}

KpiCard.displayName = "KpiCard";
