import { Navigate } from "react-router-dom";
import { useRole } from "@/features/auth/components/RoleGate";

export function RoleRedirect() {
  const role = useRole();
  if (role === "admin") {
    return <Navigate to="/admin" replace />;
  }
  return <Navigate to="/dashboard" replace />;
}
