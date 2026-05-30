import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { LoginRoute } from "@/routes/login";
import { ProtectedRoute } from "@/features/auth/ProtectedRoute";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div>Dashboard (Sprint 2+)</div>} />
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
