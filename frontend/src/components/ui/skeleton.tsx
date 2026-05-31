import { cn } from "@/lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Render an ECG-line shimmer instead of the default pulse rectangle.
   * Useful for table rows / detail panels where a flat block looks lifeless.
   */
  variant?: "block" | "ecg";
}

function Skeleton({ className, variant = "block", ...props }: SkeletonProps) {
  if (variant === "ecg") {
    return (
      <div
        role="status"
        aria-label="Memuat..."
        className={cn(
          "relative overflow-hidden rounded-sm bg-sunken",
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
  return (
    <div
      role="status"
      aria-label="Memuat..."
      className={cn("animate-pulse rounded-sm bg-muted", className)}
      {...props}
    />
  );
}

export { Skeleton };
