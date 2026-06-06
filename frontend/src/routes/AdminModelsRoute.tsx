import { RoleGate } from "@/features/auth/components/RoleGate";
import { ModelListPage } from "@/features/admin/pages/ModelListPage";

export function AdminModelsRoute() {
  return (
    <RoleGate allow={["admin"]}>
      <ModelListPage />
    </RoleGate>
  );
}
