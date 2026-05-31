import * as React from "react";

import { cn } from "@/lib/utils";

/*
 * Document-card pattern (ADR-0011 compliant): sharp radius, prominent border,
 * near-zero shadow. Mirrors a clinical lab report rather than a SaaS card.
 * The header supports an optional section-label slot (icon + uppercase label)
 * that gives each Card a one-line domain marker.
 */

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-sm border border-border-strong bg-card text-card-foreground",
        "shadow-[0_1px_0_rgb(0_0_0_/_0.04)]",
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
    <div ref={ref} className={cn("flex flex-col space-y-1 p-4", className)} {...props}>
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
    <div ref={ref} className={cn("p-4 pt-0", className)} {...props} />
  ),
);
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center p-4 pt-0", className)} {...props} />
  ),
);
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
