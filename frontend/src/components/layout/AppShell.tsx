import { useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { ClipboardList, LayoutDashboard, Menu, Users, type LucideIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

import { Breadcrumb } from "./Breadcrumb";
import { Header } from "./Header";

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
}

const navSections: { title: string; items: NavItem[] }[] = [
  {
    title: "Klinis",
    items: [
      { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { to: "/patients", label: "Pasien", icon: Users },
    ],
  },
];

interface SidebarNavProps {
  /** Called whenever a nav link is clicked (used to close mobile drawer). */
  onNavigate?: () => void;
}

function SidebarNav({ onNavigate }: SidebarNavProps) {
  const { pathname } = useLocation();
  return (
    <nav aria-label="Navigasi utama" className="flex flex-col gap-4 px-3 py-4">
      {navSections.map((section) => (
        <div key={section.title} className="flex flex-col gap-1">
          <div className="section-label px-2 pb-1">{section.title}</div>
          {section.items.map((item) => {
            const active = pathname.startsWith(item.to);
            const Icon = item.icon;
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={onNavigate}
                className={cn(
                  "group relative flex items-center gap-2 px-3 py-1.5 text-sm",
                  "rounded-sm transition-colors duration-150",
                  active
                    ? "bg-affirmed-soft text-primary font-medium"
                    : "text-foreground hover:bg-sunken",
                )}
                aria-current={active ? "page" : undefined}
              >
                {/* Left accent bar — clinical, not bg-fill. */}
                <span
                  aria-hidden="true"
                  className={cn(
                    "absolute left-0 top-1 bottom-1 w-0.5 rounded-sm transition-colors",
                    active ? "bg-primary" : "bg-transparent",
                  )}
                />
                <Icon className="h-4 w-4 shrink-0" aria-hidden={true} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      ))}
    </nav>
  );
}

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col bg-sunken">
      {/* Skip-to-content for keyboard users (a11y). */}
      <a
        href="#main-content"
        className={cn(
          "sr-only focus:not-sr-only",
          "focus:absolute focus:left-3 focus:top-3 focus:z-50",
          "focus:rounded-sm focus:bg-foreground focus:px-3 focus:py-1.5",
          "focus:text-sm focus:text-background focus:shadow",
        )}
      >
        Lewati ke konten utama
      </a>

      <Header
        leading={
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                aria-label="Buka menu navigasi"
              >
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 border-r border-border-strong bg-paper p-0">
              <div className="flex h-14 items-center gap-2 border-b border-border-strong px-4">
                <ClipboardList className="h-4 w-4 text-primary" aria-hidden="true" />
                <span className="text-base font-semibold tracking-tight">EKG-Insight</span>
              </div>
              <SidebarNav onNavigate={() => setMobileOpen(false)} />
            </SheetContent>
          </Sheet>
        }
      />

      <div className="flex flex-1">
        {/* Desktop sidebar. */}
        <aside className="no-print hidden w-56 shrink-0 border-r border-border-strong bg-paper md:block">
          <SidebarNav />
        </aside>

        <main
          id="main-content"
          tabIndex={-1}
          className="flex-1 overflow-auto bg-sunken px-4 py-4 md:px-6 md:py-5"
        >
          <Breadcrumb className="mb-3" />
          <Outlet />
        </main>
      </div>
    </div>
  );
}
