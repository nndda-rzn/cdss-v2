import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { LoginRoute } from "@/routes/login";
import { NotFoundRoute } from "@/routes/NotFoundRoute";
import { ProtectedRoute } from "@/features/auth/components/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { FocusShell } from "@/components/layout/FocusShell";
import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";
import { PatientRegisterRoute } from "@/routes/PatientRegisterRoute";
import { PatientsRoute } from "@/routes/PatientsRoute";
import { PatientDetailRoute } from "@/routes/PatientDetailRoute";
import { EncounterCreateRoute } from "@/routes/EncounterCreateRoute";
import { EncounterDetailRoute } from "@/routes/EncounterDetailRoute";
import { AnalysisDetailRoute } from "@/routes/AnalysisDetailRoute";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/patients" element={<PatientsRoute />} />
            <Route path="/patients/new" element={<PatientRegisterRoute />} />
            <Route path="/patients/:id" element={<PatientDetailRoute />} />
            <Route path="/patients/:id/encounters/new" element={<EncounterCreateRoute />} />
            <Route path="/encounters/:id" element={<EncounterDetailRoute />} />
          </Route>
          <Route element={<FocusShell />}>
            <Route
              path="/encounters/:id/ecg-studies/:studyId/analyses"
              element={<AnalysisDetailRoute />}
            />
          </Route>
        </Route>
        <Route path="*" element={<NotFoundRoute />} />
      </Routes>
    </BrowserRouter>
  );
}
