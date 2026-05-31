import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

import type { VitalStatus } from "./ranges";

const TONE: Record<VitalStatus, string> = {
  ok: "border-border-strong bg-paper",
  caution: "border-amber-500/30 bg-caution-soft",
  negative: "border-wine-500/30 bg-negative-soft",
  unknown: "border-dashed border-border bg-sunken",
};

const DOT: Record<VitalStatus, string> = {
  ok: "bg-affirmed",
  caution: "bg-caution",
  negative: "bg-negative",
  unknown: "bg-charcoal-300",
};

export interface MiniCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  unit?: string;
  status: VitalStatus;
}

/** A single clinical vital reading rendered as a compact status card. */
export function MiniCard({ icon: Icon, label, value, unit, status }: MiniCardProps) {
  return (
    <div className={cn("flex flex-col gap-1 rounded-sm border px-3 py-2", TONE[status])}>
      <div className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
        <Icon className="h-3.5 w-3.5" aria-hidden={true} />
        <span>{label}</span>
        <span aria-hidden="true" className={cn("ml-auto h-1.5 w-1.5 rounded-full", DOT[status])} />
      </div>
      <div className="flex items-baseline gap-1">
        <span className="tabular text-lg font-semibold text-foreground">{value}</span>
        {unit && <span className="text-xs text-muted-foreground">{unit}</span>}
      </div>
    </div>
  );
}

MiniCard.displayName = "MiniCard";
