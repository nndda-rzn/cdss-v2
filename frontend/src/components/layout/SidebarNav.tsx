import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, Users, Building2, ClipboardList, type LucideIcon } from "lucide-react";

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useRole } from "@/features/auth/components/RoleGate";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

interface NavItem {
  to: string;
  /** Indonesian label. EN comes from `t()` mapping below. */
  label: string;
  labelEn: string;
  icon: LucideIcon;
  exact?: boolean;
}

const BASE_SECTIONS: { titleId: string; titleEn: string; items: NavItem[] }[] = [
  {
    titleId: "Klinis",
    titleEn: "Clinical",
    items: [
      { to: "/dashboard", label: "Dashboard", labelEn: "Dashboard", icon: LayoutDashboard },
      { to: "/patients", label: "Pasien", labelEn: "Patients", icon: Users },
      { to: "/encounters", label: "Kunjungan", labelEn: "Encounters", icon: ClipboardList },
    ],
  },
];

const ADMIN_SECTION = {
  titleId: "Admin",
  titleEn: "Admin",
  items: [
    { to: "/admin", label: "Dashboard", labelEn: "Dashboard", icon: LayoutDashboard, exact: true },
    { to: "/admin/users", label: "User", labelEn: "Users", icon: Users },
    { to: "/admin/facilities", label: "Fasilitas", labelEn: "Facilities", icon: Building2 },
  ],
};

export interface SidebarNavProps {
  /** Render in icon-only collapsed mode (uses tooltips for labels). */
  collapsed?: boolean;
  /** Called when a nav link is clicked (used to close the mobile drawer). */
  onNavigate?: () => void;
}

export function SidebarNav({ collapsed = false, onNavigate }: SidebarNavProps) {
  const { pathname } = useLocation();
  const t = useI18nStore((s) => s.t);
  const role = useRole();
  const sections = role === "admin" ? [ADMIN_SECTION] : BASE_SECTIONS;

  return (
    <TooltipProvider delayDuration={200}>
      <nav
        aria-label={t("Navigasi utama", "Main navigation")}
        className={cn("flex flex-col gap-4 py-4", collapsed ? "px-2" : "px-3")}
      >
        {sections.map((section) => (
          <div key={section.titleId} className="flex flex-col gap-1">
            {!collapsed && (
              <div className="section-label px-2 pb-1">{t(section.titleId, section.titleEn)}</div>
            )}
            {section.items.map((item) => {
              const active = item.exact ? pathname === item.to : pathname.startsWith(item.to);
              const Icon = item.icon;
              const label = t(item.label, item.labelEn);
              const link = (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={onNavigate}
                  className={cn(
                    "group relative flex items-center gap-2 rounded-md text-sm",
                    "transition-colors duration-150",
                    collapsed ? "justify-center px-2 py-2" : "px-3 py-1.5",
                    active
                      ? "bg-affirmed-soft text-primary font-medium"
                      : "text-foreground hover:bg-sunken",
                  )}
                  aria-current={active ? "page" : undefined}
                  aria-label={collapsed ? label : undefined}
                >
                  <span
                    aria-hidden="true"
                    className={cn(
                      "absolute left-0 top-1 bottom-1 w-[3px] rounded-r-sm transition-colors",
                      active ? "bg-primary" : "bg-transparent",
                    )}
                  />
                  <Icon className="h-4 w-4 shrink-0" aria-hidden={true} />
                  {!collapsed && <span>{label}</span>}
                </Link>
              );

              if (!collapsed) return link;
              return (
                <Tooltip key={item.to}>
                  <TooltipTrigger asChild>{link}</TooltipTrigger>
                  <TooltipContent side="right" className="text-xs">
                    {label}
                  </TooltipContent>
                </Tooltip>
              );
            })}
          </div>
        ))}
      </nav>
    </TooltipProvider>
  );
}
