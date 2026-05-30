import { useNavigate } from "react-router-dom";
import { LoginForm } from "@/features/auth/LoginForm";

export function LoginRoute() {
  const navigate = useNavigate();
  return (
    <main>
      <h1>EKG-Insight</h1>
      <LoginForm onSuccess={() => navigate("/dashboard")} />
    </main>
  );
}
