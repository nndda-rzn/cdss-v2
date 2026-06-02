import { RoleGate } from "@/features/auth/components/RoleGate";
import { AdminDashboardPage } from "@/features/admin/pages/AdminDashboardPage";

export function AdminDashboardRoute() {
  return (
    <RoleGate allow={["admin"]}>
      <AdminDashboardPage />
    </RoleGate>
  );
}
