import { RoleGate } from "@/features/auth/components/RoleGate";
import { UserListPage } from "@/features/admin/pages/UserListPage";

export function AdminUsersRoute() {
  return (
    <RoleGate allow={["admin"]}>
      <UserListPage />
    </RoleGate>
  );
}
