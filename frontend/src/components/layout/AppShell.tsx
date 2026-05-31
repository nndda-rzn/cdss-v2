import { Link, Outlet, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/patients", label: "Pasien" },
];

export function AppShell() {
  const location = useLocation();
  const clear = useAuthStore((s) => s.clear);

  return (
    <div className="flex h-screen">
      <aside className="flex w-56 flex-col gap-2 border-r bg-muted/40 p-4">
        <h2 className="mb-4 text-lg font-semibold">EKG-Insight</h2>
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                "rounded-md px-3 py-2 text-sm",
                location.pathname.startsWith(item.to)
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-accent",
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto">
          <Button variant="outline" className="w-full" onClick={() => clear()}>
            Keluar
          </Button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
