import { useState } from "react";
import { Search } from "lucide-react";

import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import { GlobalSearch } from "./GlobalSearch";
import { useCommandKHotkey } from "../hooks";

/**
 * Header pill that looks like a search input. Clicking or hitting Ctrl+K
 * opens the command palette dialog. Hidden on small screens to keep the
 * mobile header compact (mobile users can still use the URL bar).
 */
export function GlobalSearchTrigger() {
  const t = useI18nStore((s) => s.t);
  const [open, setOpen] = useState(false);
  useCommandKHotkey(() => setOpen(true));

  const platform = typeof navigator !== "undefined" ? navigator.platform : "";
  const isMac = /Mac|iPad|iPhone|iPod/.test(platform);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label={t("Buka pencarian global", "Open global search")}
        className={cn(
          "hidden h-8 cursor-pointer items-center gap-2 rounded-md border border-border bg-sunken",
          "px-2.5 text-xs text-muted-foreground transition-colors",
          "hover:border-border-strong hover:bg-paper hover:text-foreground",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          "md:inline-flex md:min-w-[220px] md:justify-between",
        )}
      >
        <span className="flex items-center gap-1.5">
          <Search className="h-3.5 w-3.5" aria-hidden="true" />
          {t("Cari", "Search")}
        </span>
        <kbd className="rounded-sm border border-border-strong bg-paper px-1.5 py-0.5 font-mono text-[10px]">
          {isMac ? "⌘K" : "Ctrl K"}
        </kbd>
      </button>
      <GlobalSearch open={open} onOpenChange={setOpen} />
    </>
  );
}
