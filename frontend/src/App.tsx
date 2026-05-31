import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { LoginRoute } from "@/routes/login";
import { ProtectedRoute } from "@/features/auth/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { PatientRegisterRoute } from "@/routes/PatientRegisterRoute";
import { PatientsRoute } from "@/routes/PatientsRoute";
import { PatientDetailRoute } from "@/routes/PatientDetailRoute";
import { EncounterCreateRoute } from "@/routes/EncounterCreateRoute";
import { EncounterDetailRoute } from "@/routes/EncounterDetailRoute";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/dashboard" element={<div>Dashboard (Sprint 2+)</div>} />
            <Route path="/patients" element={<PatientsRoute />} />
            <Route path="/patients/new" element={<PatientRegisterRoute />} />
            <Route path="/patients/:id" element={<PatientDetailRoute />} />
            <Route path="/patients/:id/encounters/new" element={<EncounterCreateRoute />} />
            <Route path="/encounters/:id" element={<EncounterDetailRoute />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
