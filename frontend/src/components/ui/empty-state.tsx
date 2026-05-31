import * as React from "react";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  /** Short, action-oriented headline. */
  title: string;
  /** Optional explanatory copy. */
  description?: string;
  /** Optional action area (typically a primary Button or Link). */
  action?: React.ReactNode;
  /** Disable the EcgSweep motif (e.g. when nested in already-illustrated screens). */
  hideMotif?: boolean;
  className?: string;
}

/**
 * Empty-state pattern with the ECG signature motif. Used wherever a list or
 * panel renders zero items — patient list, encounter list, study list.
 */
export function EmptyState({ title, description, action, hideMotif, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-sm border border-dashed border-border-strong bg-paper px-6 py-10 text-center",
        className,
      )}
    >
      {!hideMotif && (
        <EcgSweep
          className="text-primary/60"
          width={140}
          height={36}
          thickness={2}
          aria-hidden="true"
        />
      )}
      <div className="flex flex-col gap-1">
        <p className="text-sm font-semibold text-foreground">{title}</p>
        {description && <p className="text-xs text-muted-foreground">{description}</p>}
      </div>
      {action && <div className="pt-1">{action}</div>}
    </div>
  );
}

EmptyState.displayName = "EmptyState";
