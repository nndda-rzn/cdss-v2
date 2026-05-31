import { useNavigate } from "react-router-dom";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoginForm } from "@/features/auth/LoginForm";

export function LoginRoute() {
  const navigate = useNavigate();
  return (
    <main className="relative flex min-h-screen items-center justify-center bg-sunken px-4">
      {/* Subtle ECG motif background aksen. */}
      <EcgSweep
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-primary/[0.04]"
        width={900}
        height={240}
        thickness={3}
      />
      <Card className="relative z-10 w-full max-w-sm">
        <CardHeader className="items-center text-center">
          <div className="mb-1 flex items-center justify-center gap-2 text-primary">
            <EcgSweep width={36} height={18} thickness={2.5} />
          </div>
          <CardTitle className="text-lg">EKG-Insight</CardTitle>
          <p className="text-xs text-muted-foreground">Clinical Decision Support System</p>
        </CardHeader>
        <CardContent>
          <LoginForm onSuccess={() => navigate("/dashboard")} />
        </CardContent>
      </Card>
    </main>
  );
}
