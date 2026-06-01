import * as React from "react";

import { cn } from "@/lib/utils";

/*
 * Card primitive — SaaS-polished pass (2026-06-01-saas-ui-polish-design.md).
 * Rounded radius (lg = 6px), subtle progressive shadow (elev-sm), and a
 * gentle shadow lift on hover. The header still supports an optional
 * section-label slot (icon + uppercase label) for one-line domain markers,
 * preserving the clinical document feel inside a more modern container.
 */

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * When true, the card lifts and shadow intensifies on hover. Use for
   * KPI cards, list rows, or anything actually clickable. Defaults to false
   * so static layout cards (patient detail, encounter info) feel stable.
   */
  interactive?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, interactive = false, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-lg border border-border bg-card text-card-foreground shadow-elev-sm",
        "transition-shadow duration-200",
        interactive && "cursor-pointer hover:shadow-elev-md hover:-translate-y-[1px]",
        interactive && "transition-all duration-200",
        className,
      )}
      {...props}
    />
  ),
);
Card.displayName = "Card";

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Optional uppercase section label rendered above the title. */
  sectionLabel?: React.ReactNode;
  /** Optional Lucide icon paired with the section label. */
  sectionIcon?: React.ReactNode;
}

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, sectionLabel, sectionIcon, children, ...props }, ref) => (
    <div ref={ref} className={cn("flex flex-col space-y-1 p-5", className)} {...props}>
      {sectionLabel && (
        <div className="section-label flex items-center gap-1.5">
          {sectionIcon}
          <span>{sectionLabel}</span>
        </div>
      )}
      {children}
    </div>
  ),
);
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("text-base font-semibold leading-tight tracking-tight", className)}
      {...props}
    />
  ),
);
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("text-sm text-muted-foreground", className)} {...props} />
  ),
);
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-5 pt-0", className)} {...props} />
  ),
);
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center p-5 pt-0", className)} {...props} />
  ),
);
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
