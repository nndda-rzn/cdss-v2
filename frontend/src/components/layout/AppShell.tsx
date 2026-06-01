import { useState } from "react";
import { Outlet } from "react-router-dom";
import { ClipboardList, Menu } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import { Breadcrumb } from "./Breadcrumb";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { SidebarNav } from "./SidebarNav";

const SIDEBAR_KEY = "ekg.sidebar.collapsed";

function loadCollapsed(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(SIDEBAR_KEY) === "1";
}

function saveCollapsed(collapsed: boolean) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(SIDEBAR_KEY, collapsed ? "1" : "0");
}

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState<boolean>(loadCollapsed);
  const t = useI18nStore((s) => s.t);

  const toggleCollapsed = () => {
    setCollapsed((prev) => {
      const next = !prev;
      saveCollapsed(next);
      return next;
    });
  };

  return (
    <div className="flex min-h-screen flex-col bg-sunken">
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

      <Header
        leading={
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                aria-label={t("Buka menu navigasi", "Open navigation menu")}
              >
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 border-r border-border-strong bg-paper p-0">
              <div className="flex h-14 items-center gap-2 border-b border-border-strong px-4">
                <ClipboardList className="h-4 w-4 text-primary" aria-hidden="true" />
                <span className="text-base font-semibold tracking-tight">CardioVision-CDSS</span>
              </div>
              <SidebarNav onNavigate={() => setMobileOpen(false)} />
            </SheetContent>
          </Sheet>
        }
      />

      <div className="flex flex-1">
        <Sidebar collapsed={collapsed} onToggle={toggleCollapsed} />
        <main
          id="main-content"
          tabIndex={-1}
          className="flex-1 overflow-auto bg-sunken px-4 py-4 md:px-6 md:py-5"
        >
          <Breadcrumb className="mb-3" />
          <div className="animate-fadeIn">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
