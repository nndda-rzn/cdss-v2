import { Link, Outlet, useParams } from "react-router-dom";
import { LogOut } from "lucide-react";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { Button } from "@/components/ui/button";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

/**
 * Sidebar-less "medical instrument" layout. Used for focused reading screens
 * (AI analysis, and later HiResCAM inspection). Minimal sticky header with the
 * brand mark and an Exit button back to the parent encounter; cool neutral
 * `bg-charcoal-50` content area. The page itself renders the patient identity
 * strip, so this shell stays dumb.
 */
export function FocusShell() {
  const { id = "" } = useParams();
  const t = useI18nStore((s) => s.t);

  return (
    <div className="flex min-h-screen flex-col bg-charcoal-50">
      <a
        href="#main-content"
        className={cn(
          "sr-only focus:not-sr-only",
          "focus:absolute focus:left-3 focus:top-3 focus:z-50",
          "focus:rounded-md focus:bg-foreground focus:px-3 focus:py-1.5",
          "focus:text-sm focus:text-background focus:shadow-elev-md",
        )}
      >
        {t("Lewati ke konten utama", "Skip to main content")}
      </a>

      <header className="no-print sticky top-0 z-30 flex h-12 items-center gap-2 border-b border-border-strong bg-paper px-4">
        <EcgSweep className="text-primary" width={24} height={12} thickness={2.5} />
        <span className="text-sm font-semibold tracking-tight">CardioVision-CDSS</span>
        <Button asChild variant="ghost" size="sm" className="ml-auto cursor-pointer">
          <Link to={`/encounters/${id}`}>
            <LogOut className="mr-1.5 h-4 w-4" aria-hidden="true" />
            {t("Keluar", "Exit")}
          </Link>
        </Button>
      </header>

      <main id="main-content" tabIndex={-1} className="flex-1 overflow-auto px-6 py-6 md:px-10">
        <div className="animate-fadeIn">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
