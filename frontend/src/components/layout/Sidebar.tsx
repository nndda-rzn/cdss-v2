import { ChevronsLeft, ChevronsRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import { SidebarNav } from "./SidebarNav";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

/**
 * Desktop sidebar (hidden on mobile, where the Sheet drawer renders the same
 * `SidebarNav` instead). Width animates between 224px (`w-56`) and 64px
 * (`w-16`); the collapse toggle lives at the bottom for thumb-reach.
 */
export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const t = useI18nStore((s) => s.t);

  return (
    <aside
      className={cn(
        "no-print hidden shrink-0 border-r border-border-strong bg-paper md:flex",
        "flex-col transition-[width] duration-200 ease-out",
        collapsed ? "w-16" : "w-56",
      )}
      aria-label={t("Sidebar", "Sidebar")}
    >
      <div className="flex-1 overflow-y-auto">
        <SidebarNav collapsed={collapsed} />
      </div>
      <div className="border-t border-border p-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggle}
          aria-label={
            collapsed ? t("Buka sidebar", "Expand sidebar") : t("Tutup sidebar", "Collapse sidebar")
          }
          aria-expanded={!collapsed}
          className={cn(
            "w-full cursor-pointer text-muted-foreground hover:text-foreground",
            collapsed ? "justify-center px-0" : "justify-start",
          )}
        >
          {collapsed ? (
            <ChevronsRight className="h-4 w-4" aria-hidden="true" />
          ) : (
            <>
              <ChevronsLeft className="mr-1.5 h-4 w-4" aria-hidden="true" />
              <span className="text-xs">{t("Tutup sidebar", "Collapse")}</span>
            </>
          )}
        </Button>
      </div>
    </aside>
  );
}
