import { EcgSweep } from "@/components/brand/EcgSweep";
import { LanguageToggle } from "@/components/layout/LanguageToggle";
import { UserMenu } from "@/components/layout/UserMenu";
import { Separator } from "@/components/ui/separator";
import { useI18nStore } from "@/lib/i18n/store";

interface HeaderProps {
  /**
   * Optional left-slot, used for the mobile menu trigger button (rendered by
   * AppShell). Keeps the responsive control out of this component.
   */
  leading?: React.ReactNode;
}

/**
 * Top header bar — sticky 56px tall. Brand mark + wordmark on the left;
 * language toggle and user menu on the right. The plain logout button moved
 * into the user dropdown so the header stays visually clean.
 */
export function Header({ leading }: HeaderProps) {
  const t = useI18nStore((s) => s.t);

  return (
    <header className="no-print sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border-strong bg-paper px-4">
      {leading}
      <div className="flex items-center gap-2 text-foreground">
        <EcgSweep className="text-primary" width={28} height={14} thickness={2.5} />
        <span className="text-base font-semibold tracking-tight">EKG-Insight</span>
      </div>
      <Separator orientation="vertical" className="h-6 bg-border-strong" />
      <span className="hidden text-xs text-muted-foreground sm:inline">
        {t("CDSS demo", "CDSS demo")}
      </span>
      <div className="ml-auto flex items-center gap-2">
        <LanguageToggle />
        <Separator orientation="vertical" className="h-6 bg-border-strong" />
        <UserMenu />
      </div>
    </header>
  );
}

Header.displayName = "Header";
