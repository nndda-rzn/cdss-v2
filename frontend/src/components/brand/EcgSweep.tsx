import * as React from "react";

import { cn } from "@/lib/utils";

interface EcgSweepProps extends React.SVGAttributes<SVGSVGElement> {
  /** Stroke colour (defaults to current text colour). */
  color?: string;
  /** Stroke width in SVG units (defaults to 2). */
  thickness?: number;
  /** Animate the sweep horizontally (respects prefers-reduced-motion via CSS). */
  animate?: boolean;
}

/*
 * Signature ECG-line motif. Single SVG path of one cardiac cycle (P-QRS-T-U)
 * sized to a 120x32 viewBox so callers can scale it via width/height or CSS.
 *
 * Used across the app for brand identity:
 *   - login background aksen
 *   - AppShell brand mark
 *   - empty-state illustration
 *   - loading shimmer
 */
export function EcgSweep({
  className,
  color,
  thickness = 2,
  animate = false,
  width = 120,
  height = 32,
  ...props
}: EcgSweepProps) {
  return (
    <svg
      role="img"
      aria-label="CardioVision-CDSS wave motif"
      viewBox="0 0 120 32"
      width={width}
      height={height}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn(animate && "animate-ecg", className)}
      {...props}
    >
      <path
        d="M0 16 H18 L22 14 L26 18 L30 13 L34 16 L42 16 L46 6 L50 26 L54 4 L58 28 L62 16 L72 16 L76 12 L80 18 L86 16 H120"
        stroke={color ?? "currentColor"}
        strokeWidth={thickness}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

EcgSweep.displayName = "EcgSweep";
