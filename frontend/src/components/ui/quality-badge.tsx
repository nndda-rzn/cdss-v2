import * as React from "react";

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

type QualityStatus = "good" | "acceptable" | "poor";

interface QualityBadgeProps {
  status: QualityStatus;
  /** Composite score 0..1; rendered with tabular numerals. */
  score?: number;
  /** Raw metrics: blur, noise, brightness, contrast (rendered in tooltip). */
  metrics?: Record<string, number>;
  className?: string;
}

const LABEL: Record<QualityStatus, string> = {
  good: "Baik",
  acceptable: "Cukup",
  poor: "Buruk",
};

const TONE: Record<QualityStatus, { dot: string; bg: string; text: string; ring: string }> = {
  good: {
    dot: "bg-affirmed",
    bg: "bg-affirmed-soft",
    text: "text-primary",
    ring: "ring-1 ring-inset ring-primary/20",
  },
  acceptable: {
    dot: "bg-caution",
    bg: "bg-caution-soft",
    text: "text-amber-700",
    ring: "ring-1 ring-inset ring-amber-700/20",
  },
  poor: {
    dot: "bg-negative",
    bg: "bg-negative-soft",
    text: "text-wine-700",
    ring: "ring-1 ring-inset ring-wine-700/20",
  },
};

/**
 * QualityBadge — clinical status pill with glyph dot, label, and optional
 * tabular score. Tooltip on hover/focus reveals the underlying metric values.
 *
 * Wrap your app once with `<TooltipProvider>` (Radix) for the hover/focus
 * tooltip to render. The component falls back to a bare badge if the parent
 * tree has no provider.
 */
export function QualityBadge({ status, score, metrics, className }: QualityBadgeProps) {
  const tone = TONE[status];
  const badge = (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-sm px-2 py-0.5 text-xs font-medium",
        tone.bg,
        tone.text,
        tone.ring,
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", tone.dot)} aria-hidden="true" />
      <span>{LABEL[status]}</span>
      {typeof score === "number" && (
        <span className="tabular text-[11px] opacity-80">{score.toFixed(2)}</span>
      )}
    </span>
  );

  if (!metrics) return badge;

  return (
    <TooltipProvider delayDuration={150}>
      <Tooltip>
        <TooltipTrigger asChild>{badge}</TooltipTrigger>
        <TooltipContent side="top" className="text-xs">
          <div className="grid grid-cols-2 gap-x-3 gap-y-0.5">
            {Object.entries(metrics).map(([key, value]) => (
              <React.Fragment key={key}>
                <span className="capitalize text-muted-foreground">{key}</span>
                <span className="tabular text-right">
                  {typeof value === "number" ? value.toFixed(1) : String(value)}
                </span>
              </React.Fragment>
            ))}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

QualityBadge.displayName = "QualityBadge";
