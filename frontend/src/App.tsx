import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { LoginRoute } from "@/routes/login";
import { ProtectedRoute } from "@/features/auth/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/dashboard" element={<div>Dashboard (Sprint 2+)</div>} />
            <Route path="/patients" element={<div>Pasien (Sprint 2A)</div>} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
