// frontend/src/routes/TuningRoute.tsx
import { lazy } from "react";

const TuningGridPage = lazy(() =>
  import("../features/tuning/pages/TuningGridPage").then((m) => ({ default: m.TuningGridPage })),
);

export function TuningRoute() {
  return <TuningGridPage />;
}
