import { cn } from "@/lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * - `block` (default): plain pulsing rectangle.
   * - `ecg`: ECG-line shimmer (clinical motif) — better for table rows.
   * - `card`: rounded-lg pulsing block sized for KPI/dashboard cards.
   */
  variant?: "block" | "ecg" | "card";
}

function Skeleton({ className, variant = "block", ...props }: SkeletonProps) {
  if (variant === "ecg") {
    return (
      <div
        role="status"
        aria-label="Memuat..."
        className={cn(
          "relative overflow-hidden rounded-md bg-sunken",
          "before:absolute before:inset-0 before:-translate-x-full",
          "before:animate-[shimmer_1.6s_infinite]",
          "before:bg-gradient-to-r before:from-transparent before:via-primary/15 before:to-transparent",
          "motion-reduce:before:animate-none",
          className,
        )}
        {...props}
      />
    );
  }
  if (variant === "card") {
    return (
      <div
        role="status"
        aria-label="Memuat..."
        className={cn("animate-pulse rounded-lg bg-sunken shadow-elev-sm", className)}
        {...props}
      />
    );
  }
  return (
    <div
      role="status"
      aria-label="Memuat..."
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  );
}

export { Skeleton };
