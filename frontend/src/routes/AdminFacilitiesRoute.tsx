import { RoleGate } from "@/features/auth/components/RoleGate";
import { FacilityListPage } from "@/features/admin/pages/FacilityListPage";

export function AdminFacilitiesRoute() {
  return (
    <RoleGate allow={["admin"]}>
      <FacilityListPage />
    </RoleGate>
  );
}
