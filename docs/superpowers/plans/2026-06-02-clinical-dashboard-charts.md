# Clinical Dashboard Charts Plan (SaaS + Clinical Style)

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 3 charts to clinical dashboard: encounter trend (line), diagnosis distribution (donut), ECG quality (bar). SaaS-style matching existing design system.

**Architecture:** Extend `GET /api/dashboard/stats` backend endpoint. Frontend uses `recharts` library with existing design tokens (petrol-700 primary, semantic colors).

**Tech Stack:** Flask, SQLAlchemy, React, TanStack Query, Recharts.

---

## File Structure

### Backend — Modify
| File | Change |
|------|--------|
| `backend/app/api/dashboard.py` | Add `encounter_trend`, `diagnosis_distribution`, `ecg_quality_distribution` |
| `backend/tests/integration/test_dashboard_api.py` | Add chart data tests |

### Frontend — Create
| File | Responsibility |
|------|---------------|
| `frontend/src/features/dashboard/components/EncounterTrendChart.tsx` | Line chart 7 days |
| `frontend/src/features/dashboard/components/DiagnosisDistributionChart.tsx` | Donut chart |
| `frontend/src/features/dashboard/components/EcgQualityChart.tsx` | Bar chart |

### Frontend — Modify
| File | Change |
|------|--------|
| `frontend/package.json` | Install `recharts` |
| `frontend/src/features/dashboard/types.ts` | Add chart types |
| `frontend/src/features/dashboard/pages/DashboardPage.tsx` | Add chart section |

---

## Task 1: Install recharts

- [ ] **Step 1: Install**

Run: `cd frontend && npm install recharts`

- [ ] **Step 2: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore(deps): add recharts for clinical dashboard charts"
```

---

## Task 2: Backend — Extend stats endpoint

- [ ] **Step 1: Write failing tests**

```python
# Add to tests/integration/test_dashboard_api.py

class TestDashboardChartData:
    def test_encounter_trend_returns_7_days(self, client, seeded_admin, session):
        resp = client.get("/api/dashboard/stats",
                          headers={"Authorization": f"Bearer {_admin_token()}"})
        data = resp.get_json()
        assert "encounter_trend" in data
        assert len(data["encounter_trend"]) == 7
        assert "date" in data["encounter_trend"][0]
        assert "count" in data["encounter_trend"][0]

    def test_diagnosis_distribution(self, client, seeded_admin, session):
        resp = client.get("/api/dashboard/stats",
                          headers={"Authorization": f"Bearer {_admin_token()}"})
        data = resp.get_json()
        assert "diagnosis_distribution" in data
        assert "normal" in data["diagnosis_distribution"]

    def test_ecg_quality_distribution(self, client, seeded_admin, session):
        resp = client.get("/api/dashboard/stats",
                          headers={"Authorization": f"Bearer {_admin_token()}"})
        data = resp.get_json()
        assert "ecg_quality_distribution" in data
        assert "good" in data["ecg_quality_distribution"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/integration/test_dashboard_api.py -v`

- [ ] **Step 3: Implement**

Extend `dashboard.py` `get_stats()` with 3 new queries:

```python
# Encounter trend (7 days)
encounter_trend = []
for i in range(7):
    day = today - timedelta(days=6 - i)
    next_day = day + timedelta(days=1)
    count = s.scalar(
        select(func.count(Encounter.id))
        .where(Encounter.facility_id == facility_id)
        .where(Encounter.started_at >= day)
        .where(Encounter.started_at < next_day)
    ) or 0
    encounter_trend.append({"date": day.strftime("%Y-%m-%d"), "count": count})

# Diagnosis distribution
diagnosis_rows = s.execute(
    select(AIAnalysis.predicted_class, func.count(AIAnalysis.id))
    .join(ECGStudy, ECGStudy.id == AIAnalysis.ecg_study_id)
    .join(Encounter, Encounter.id == ECGStudy.encounter_id)
    .where(Encounter.facility_id == facility_id)
    .group_by(AIAnalysis.predicted_class)
).all()
diagnosis_distribution = {row[0]: row[1] for row in diagnosis_rows}

# ECG quality distribution
quality_rows = s.execute(
    select(ECGStudy.quality_status, func.count(ECGStudy.id))
    .join(Encounter, Encounter.id == ECGStudy.encounter_id)
    .where(Encounter.facility_id == facility_id)
    .group_by(ECGStudy.quality_status)
).all()
ecg_quality_distribution = {row[0]: row[1] for row in quality_rows}
```

- [ ] **Step 4: Run tests**

Run: `cd backend && python -m pytest tests/integration/test_dashboard_api.py -v`

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/dashboard.py backend/tests/integration/test_dashboard_api.py
git commit -m "feat(dashboard): add chart data to stats endpoint"
```

---

## Task 3: Frontend — Update types

- [ ] **Step 1: Add chart types**

In `frontend/src/features/dashboard/types.ts`, add:

```typescript
export interface EncounterTrendEntry {
  date: string;
  count: number;
}

export interface DashboardStats {
  total_patients: number;
  active_encounters: number;
  analyses_today: number;
  pending_tasks: number;
  recent_encounters: RecentEncounter[];
  encounter_trend: EncounterTrendEntry[];
  diagnosis_distribution: Record<string, number>;
  ecg_quality_distribution: Record<string, number>;
}
```

- [ ] **Step 2: Verify TypeScript**

Run: `cd frontend && npx tsc --noEmit`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/dashboard/types.ts
git commit -m "feat(dashboard): add chart data types"
```

---

## Task 4: EncounterTrendChart

- [ ] **Step 1: Create component**

```tsx
// frontend/src/features/dashboard/components/EncounterTrendChart.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import type { EncounterTrendEntry } from "../types";

interface Props {
  data: EncounterTrendEntry[];
  loading?: boolean;
}

export function EncounterTrendChart({ data, loading }: Props) {
  const t = useI18nStore((s) => s.t);

  if (loading) {
    return (
      <Card>
        <CardHeader><Skeleton className="h-5 w-48" /></CardHeader>
        <CardContent><Skeleton className="h-48 w-full" /></CardContent>
      </Card>
    );
  }

  const today = data[data.length - 1]?.count ?? 0;
  const yesterday = data[data.length - 2]?.count ?? 0;
  const diff = today - yesterday;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Tren Kunjungan (7 Hari)", "Encounter Trend (7 Days)")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="date"
                tickFormatter={(v) => new Date(v).toLocaleDateString("id-ID", { weekday: "short" })}
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
              />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--paper))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "6px",
                }}
              />
              <Area
                type="monotone"
                dataKey="count"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary) / 0.1)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          {diff >= 0 ? `↑ ${diff}` : `↓ ${Math.abs(diff)}`} {t("dari kemarin", "vs yesterday")}
        </p>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/dashboard/components/EncounterTrendChart.tsx
git commit -m "feat(dashboard): add EncounterTrendChart"
```

---

## Task 5: DiagnosisDistributionChart

- [ ] **Step 1: Create component**

```tsx
// frontend/src/features/dashboard/components/DiagnosisDistributionChart.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface Props {
  data: Record<string, number>;
  loading?: boolean;
}

const COLORS: Record<string, string> = {
  normal: "hsl(142, 76%, 36%)",
  mi: "hsl(0, 84%, 60%)",
  abnormal: "hsl(38, 92%, 50%)",
};

const LABELS: Record<string, { id: string; en: string }> = {
  normal: { id: "Normal", en: "Normal" },
  mi: { id: "MI", en: "MI" },
  abnormal: { id: "Abnormal", en: "Abnormal" },
};

export function DiagnosisDistributionChart({ data, loading }: Props) {
  const t = useI18nStore((s) => s.t);

  if (loading) {
    return (
      <Card>
        <CardHeader><Skeleton className="h-5 w-48" /></CardHeader>
        <CardContent><Skeleton className="h-48 w-full" /></CardContent>
      </Card>
    );
  }

  const total = Object.values(data).reduce((a, b) => a + b, 0);
  const chartData = Object.entries(data).map(([key, value]) => ({
    name: LABELS[key]?.id ?? key,
    value,
    color: COLORS[key] ?? "hsl(var(--muted-foreground))",
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Distribusi Diagnosis AI", "AI Diagnosis Distribution")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          {t(`Total: ${total} analisis`, `Total: ${total} analyses`)}
        </p>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/dashboard/components/DiagnosisDistributionChart.tsx
git commit -m "feat(dashboard): add DiagnosisDistributionChart"
```

---

## Task 6: EcgQualityChart

- [ ] **Step 1: Create component**

```tsx
// frontend/src/features/dashboard/components/EcgQualityChart.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface Props {
  data: Record<string, number>;
  loading?: boolean;
}

const COLORS: Record<string, string> = {
  good: "hsl(142, 76%, 36%)",
  acceptable: "hsl(38, 92%, 50%)",
  poor: "hsl(0, 84%, 60%)",
};

const LABELS: Record<string, { id: string; en: string }> = {
  good: { id: "Baik", en: "Good" },
  acceptable: { id: "Cukup", en: "Acceptable" },
  poor: { id: "Buruk", en: "Poor" },
};

export function EcgQualityChart({ data, loading }: Props) {
  const t = useI18nStore((s) => s.t);

  if (loading) {
    return (
      <Card>
        <CardHeader><Skeleton className="h-5 w-48" /></CardHeader>
        <CardContent><Skeleton className="h-32 w-full" /></CardContent>
      </Card>
    );
  }

  const total = Object.values(data).reduce((a, b) => a + b, 0);
  const chartData = Object.entries(data).map(([key, value]) => ({
    name: LABELS[key]?.id ?? key,
    value,
    color: COLORS[key] ?? "hsl(var(--muted-foreground))",
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Kualitas ECG", "ECG Quality")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-32">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <YAxis type="category" dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} width={80} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--paper))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "6px",
                }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          {t(`Total: ${total} ECG`, `Total: ${total} ECG`)}
        </p>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/dashboard/components/EcgQualityChart.tsx
git commit -m "feat(dashboard): add EcgQualityChart"
```

---

## Task 7: Update DashboardPage

- [ ] **Step 1: Add chart imports and section**

In `DashboardPage.tsx`, add imports and chart section between KPI cards and Quick Actions.

- [ ] **Step 2: Verify TypeScript**

Run: `cd frontend && npx tsc --noEmit`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/dashboard/pages/DashboardPage.tsx
git commit -m "feat(dashboard): integrate charts into clinical dashboard"
```

---

## Task 8: Full test suite

- [ ] **Step 1: Backend** `cd backend && python -m pytest -v`
- [ ] **Step 2: Frontend** `cd frontend && npx vitest run`
- [ ] **Step 3: Build** `cd frontend && npx tsc -b && npx vite build`
