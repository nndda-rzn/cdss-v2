import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
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
import { EncountersRoute } from "@/routes/EncountersRoute";
import { EncounterDetailRoute } from "@/routes/EncounterDetailRoute";
import { AnalysisDetailRoute } from "@/routes/AnalysisDetailRoute";
import { AdminUsersRoute } from "@/routes/AdminUsersRoute";
import { AdminFacilitiesRoute } from "@/routes/AdminFacilitiesRoute";
import { AdminDashboardRoute } from "@/routes/AdminDashboardRoute";
import { AdminModelsRoute } from "@/routes/AdminModelsRoute";
import { RoleRedirect } from "@/features/auth/components/RoleRedirect";

export function App() {
  return (
    <BrowserRouter>
      <Toaster />
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/" element={<RoleRedirect />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/patients" element={<PatientsRoute />} />
            <Route path="/patients/new" element={<PatientRegisterRoute />} />
            <Route path="/patients/:id" element={<PatientDetailRoute />} />
            <Route path="/patients/:id/encounters/new" element={<EncounterCreateRoute />} />
            <Route path="/encounters" element={<EncountersRoute />} />
            <Route path="/encounters/:id" element={<EncounterDetailRoute />} />
            <Route path="/admin" element={<AdminDashboardRoute />} />
            <Route path="/admin/users" element={<AdminUsersRoute />} />
            <Route path="/admin/facilities" element={<AdminFacilitiesRoute />} />
            <Route path="/admin/models" element={<AdminModelsRoute />} />
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
