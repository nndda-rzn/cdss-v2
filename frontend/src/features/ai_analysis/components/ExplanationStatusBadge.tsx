import { CheckCircle2, TriangleAlert, XCircle } from "lucide-react";

import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import { STATUS_CHIP, STATUS_LABEL, STATUS_LABEL_EN } from "../labels";
import type { ExplanationStatus } from "../types";

interface Props {
  status: ExplanationStatus;
  focusMetric?: number;
  className?: string;
}

const ICONS: Record<ExplanationStatus, React.ReactNode> = {
  good: <CheckCircle2 className="h-3.5 w-3.5" />,
  diffuse: <TriangleAlert className="h-3.5 w-3.5" />,
  "off-target": <XCircle className="h-3.5 w-3.5" />,
  "low-confidence": <TriangleAlert className="h-3.5 w-3.5" />,
  "need-review": <TriangleAlert className="h-3.5 w-3.5" />,
};

export function ExplanationStatusBadge({ status, focusMetric, className }: Props) {
  const t = useI18nStore((s) => s.t);

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-sm px-2 py-0.5 text-xs font-medium",
        STATUS_CHIP[status],
        className,
      )}
    >
      {ICONS[status]}
      <span>{t(STATUS_LABEL[status], STATUS_LABEL_EN[status])}</span>
      {focusMetric !== undefined && (
        <span className="tabular text-[10px] opacity-75">{Math.round(focusMetric * 100)}%</span>
      )}
    </span>
  );
}
