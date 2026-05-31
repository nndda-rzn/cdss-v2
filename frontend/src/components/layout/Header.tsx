import { LogOut } from "lucide-react";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/features/auth/store";

interface HeaderProps {
  /**
   * Optional left-slot, used for the mobile menu trigger button (rendered by
   * AppShell). Keeps the responsive control out of this component.
   */
  leading?: React.ReactNode;
}

/**
 * Top header bar: brand mark + wordmark on the left, user controls on the
 * right. Sticky 56px tall, sits above the sidebar + main content.
 *
 * The role label is read from the auth store (decoded into the JWT). The
 * facility name is not yet available client-side; once a `/api/me` endpoint
 * exists we can replace the placeholder.
 */
export function Header({ leading }: HeaderProps) {
  const clear = useAuthStore((s) => s.clear);

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border-strong bg-paper px-4">
      {leading}
      <div className="flex items-center gap-2 text-foreground">
        <EcgSweep className="text-primary" width={28} height={14} thickness={2.5} />
        <span className="text-base font-semibold tracking-tight">EKG-Insight</span>
      </div>
      <Separator orientation="vertical" className="h-6 bg-border-strong" />
      <span className="hidden text-xs text-muted-foreground sm:inline">CDSS demo</span>
      <div className="ml-auto flex items-center gap-2">
        <Button variant="ghost" size="sm" className="cursor-pointer" onClick={() => clear()}>
          <LogOut className="mr-1.5 h-4 w-4" aria-hidden="true" />
          Keluar
        </Button>
      </div>
    </header>
  );
}

Header.displayName = "Header";
