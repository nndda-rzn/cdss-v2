# Admin Dashboard Implementation Plan (Cloudflare-style)

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cloudflare-style admin dashboard with system monitoring, clinical activity, AI performance metrics, and quick actions.

**Architecture:** Single `GET /api/admin/stats` backend endpoint returns all dashboard data. Frontend renders Cloudflare-style layout with KPI cards, gauges, line charts, and audit table.

**Tech Stack:** Flask Blueprint, SQLAlchemy, React, TanStack Query, SVG mini-charts, existing UI components (Card, Skeleton).

---

## File Structure

### Backend — Create
| File | Responsibility |
|------|---------------|
| `backend/app/api/admin/stats.py` | `GET /api/admin/stats` endpoint |
| `backend/tests/unit/api/test_admin_stats.py` | Stats endpoint tests |

### Backend — Modify
| File | Change |
|------|--------|
| `backend/app/api/admin/__init__.py` | Register `stats_bp` |

### Frontend — Create
| File | Responsibility |
|------|---------------|
| `frontend/src/features/admin/components/AdminKpiCard.tsx` | KPI card with trend indicator |
| `frontend/src/features/admin/components/AiPerformanceChart.tsx` | Line charts for AI metrics |
| `frontend/src/features/admin/components/RecentAuditTable.tsx` | Recent activity table |

### Frontend — Modify
| File | Change |
|------|--------|
| `frontend/src/features/admin/types.ts` | Add `AdminStats` type |
| `frontend/src/features/admin/api.ts` | Add `fetchAdminStats()` |
| `frontend/src/features/admin/pages/AdminDashboardPage.tsx` | Rewrite with Cloudflare layout |

---

## Task 1: Backend — `GET /api/admin/stats`

**Files:**
- Create: `backend/app/api/admin/stats.py`
- Create: `backend/tests/unit/api/test_admin_stats.py`
- Modify: `backend/app/api/admin/__init__.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/unit/api/test_admin_stats.py
"""Tests for admin dashboard stats endpoint."""
from app.core.security.jwt import make_access_token


def _admin_token():
    return make_access_token(user_id=1, role="admin", facility_id=1)


class TestAdminStats:
    def test_stats_returns_all_sections(self, client, seeded_admin, session):
        resp = client.get("/api/admin/stats",
                          headers={"Authorization": f"Bearer {_admin_token()}"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "users" in data
        assert "facilities" in data
        assert "ai" in data
        assert "audit" in data

    def test_stats_rejects_non_admin(self, client, seeded_admin):
        nurse_token = make_access_token(user_id=2, role="nurse", facility_id=1)
        resp = client.get("/api/admin/stats",
                          headers={"Authorization": f"Bearer {nurse_token}"})
        assert resp.status_code == 403
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/api/test_admin_stats.py -v`
Expected: FAIL — no `/api/admin/stats` endpoint

- [ ] **Step 3: Implement stats endpoint**

```python
# backend/app/api/admin/stats.py
"""Admin dashboard stats endpoint."""
from __future__ import annotations

from datetime import UTC, datetime, time, timedelta

from flask import Blueprint, jsonify
from sqlalchemy import func, select

from app.api._shared import session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.ai_analysis import AIAnalysis
from app.db.models.audit_log import AuditLog
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.facility import HealthcareFacility
from app.db.models.model_metadata import ModelMetadata
from app.db.models.patient import Patient
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User

bp = Blueprint("admin_stats", __name__, url_prefix="/stats")


def _start_of_today_utc() -> datetime:
    return datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)


@bp.get("")
@require_role(Role.ADMIN)
def get_stats():
    s = session()
    today = _start_of_today_utc()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)

    # Users
    total_users = s.scalar(select(func.count(User.id))) or 0
    active_users = s.scalar(
        select(func.count(User.id)).where(User.is_active.is_(True))
    ) or 0
    by_role = {}
    for role_name, count in s.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    ).all():
        by_role[role_name] = count

    # Facilities
    total_facilities = s.scalar(select(func.count(HealthcareFacility.id))) or 0

    # Active sessions
    active_sessions = s.scalar(
        select(func.count(RefreshToken.id))
        .where(RefreshToken.revoked_at.is_(None))
        .where(RefreshToken.expires_at > datetime.now(UTC))
    ) or 0

    # Active model
    active_model = s.scalar(
        select(ModelMetadata).where(ModelMetadata.is_active.is_(True)).limit(1)
    )

    # Patients
    total_patients = s.scalar(select(func.count(Patient.id))) or 0

    # Encounters
    encounters_today = s.scalar(
        select(func.count(Encounter.id)).where(Encounter.started_at >= today)
    ) or 0
    encounters_yesterday = s.scalar(
        select(func.count(Encounter.id))
        .where(Encounter.started_at >= yesterday)
        .where(Encounter.started_at < today)
    ) or 0

    # ECG Studies
    ecg_today = s.scalar(
        select(func.count(ECGStudy.id)).where(ECGStudy.acquired_at >= today)
    ) or 0
    ecg_yesterday = s.scalar(
        select(func.count(ECGStudy.id))
        .where(ECGStudy.acquired_at >= yesterday)
        .where(ECGStudy.acquired_at < today)
    ) or 0

    # AI Performance
    ai_today = s.scalar(
        select(func.count(AIAnalysis.id)).where(AIAnalysis.created_at >= today)
    ) or 0
    ai_yesterday = s.scalar(
        select(func.count(AIAnalysis.id))
        .where(AIAnalysis.created_at >= yesterday)
        .where(AIAnalysis.created_at < today)
    ) or 0

    avg_inference = s.scalar(
        select(func.avg(AIAnalysis.inference_time_ms))
        .where(AIAnalysis.created_at >= week_ago)
    ) or 0

    avg_confidence = s.scalar(
        select(func.avg(AIAnalysis.confidence_score))
        .where(AIAnalysis.created_at >= week_ago)
    ) or 0

    # AI trend (7 days)
    inference_trend = []
    confidence_trend = []
    for i in range(7):
        day = today - timedelta(days=6 - i)
        next_day = day + timedelta(days=1)
        day_avg_ms = s.scalar(
            select(func.avg(AIAnalysis.inference_time_ms))
            .where(AIAnalysis.created_at >= day)
            .where(AIAnalysis.created_at < next_day)
        )
        day_avg_conf = s.scalar(
            select(func.avg(AIAnalysis.confidence_score))
            .where(AIAnalysis.created_at >= day)
            .where(AIAnalysis.created_at < next_day)
        )
        inference_trend.append({
            "date": day.strftime("%Y-%m-%d"),
            "avg_ms": round(float(day_avg_ms), 1) if day_avg_ms else None,
        })
        confidence_trend.append({
            "date": day.strftime("%Y-%m-%d"),
            "avg": round(float(day_avg_conf), 3) if day_avg_conf else None,
        })

    # Recent audit (last 10)
    audit_rows = s.scalars(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(10)
    ).all()
    audit = [
        {
            "user_id": a.user_id,
            "action": a.action,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in audit_rows
    ]

    return jsonify(
        users={"total": total_users, "active": active_users, "by_role": by_role},
        facilities={"total": total_facilities},
        sessions={"active": active_sessions},
        model={
            "name": active_model.model_name if active_model else None,
            "version": active_model.model_version if active_model else None,
            "is_active": active_model is not None,
        },
        patients={"total": total_patients},
        encounters={"today": encounters_today, "yesterday": encounters_yesterday},
        ecg={"today": ecg_today, "yesterday": ecg_yesterday},
        ai={
            "analyses_today": ai_today,
            "yesterday": ai_yesterday,
            "avg_inference_ms": round(float(avg_inference), 1),
            "avg_confidence": round(float(avg_confidence), 3),
            "inference_trend": inference_trend,
            "confidence_trend": confidence_trend,
        },
        audit=audit,
    )
```

- [ ] **Step 4: Register blueprint**

In `backend/app/api/admin/__init__.py`, add:

```python
from app.api.admin.stats import bp as stats_bp

admin_bp.register_blueprint(stats_bp)
```

- [ ] **Step 5: Run tests**

Run: `cd backend && python -m pytest tests/unit/api/test_admin_stats.py -v`
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/admin/stats.py backend/app/api/admin/__init__.py backend/tests/unit/api/test_admin_stats.py
git commit -m "feat(api): add admin dashboard stats endpoint"
```

---

## Task 2: Frontend — AdminStats types + API

**Files:**
- Modify: `frontend/src/features/admin/types.ts`
- Modify: `frontend/src/features/admin/api.ts`

- [ ] **Step 1: Add AdminStats type**

In `frontend/src/features/admin/types.ts`, add:

```typescript
export interface AdminAiStats {
  analyses_today: number;
  yesterday: number;
  avg_inference_ms: number;
  avg_confidence: number;
  inference_trend: { date: string; avg_ms: number | null }[];
  confidence_trend: { date: string; avg: number | null }[];
}

export interface AdminAuditEntry {
  user_id: number | null;
  action: string;
  entity_type: string | null;
  entity_id: number | null;
  created_at: string | null;
}

export interface AdminStats {
  users: { total: number; active: number; by_role: Record<string, number> };
  facilities: { total: number };
  sessions: { active: number };
  model: { name: string | null; version: string | null; is_active: boolean };
  patients: { total: number };
  encounters: { today: number; yesterday: number };
  ecg: { today: number; yesterday: number };
  ai: AdminAiStats;
  audit: AdminAuditEntry[];
}
```

- [ ] **Step 2: Add fetchAdminStats + adminKeys.stats**

In `frontend/src/features/admin/api.ts`, add:

```typescript
import type { AdminStats } from "./types";

// In adminKeys, add:
export const adminKeys = {
  users: ["admin", "users"] as const,
  facilities: ["admin", "facilities"] as const,
  stats: ["admin", "stats"] as const,
};

// New function:
export async function fetchAdminStats(): Promise<AdminStats> {
  const resp = await apiFetch("/api/admin/stats");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to load stats");
  return body;
}
```

- [ ] **Step 3: Verify TypeScript**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/admin/types.ts frontend/src/features/admin/api.ts
git commit -m "feat(admin): add AdminStats type and fetchAdminStats API"
```

---

## Task 3: Frontend — AdminKpiCard

**Files:**
- Create: `frontend/src/features/admin/components/AdminKpiCard.tsx`

- [ ] **Step 1: Create component**

```tsx
import { type LucideIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface Props {
  label: string;
  value: number | string;
  icon: LucideIcon;
  hint?: string;
  trend?: { value: number; label: string };
  loading?: boolean;
}

export function AdminKpiCard({ label, value, icon: Icon, hint, trend, loading }: Props) {
  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-4" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-16" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{label}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {trend && (
          <p className={cn(
            "text-xs",
            trend.value > 0 ? "text-green-600" : trend.value < 0 ? "text-red-600" : "text-muted-foreground",
          )}>
            {trend.value > 0 ? "↑" : trend.value < 0 ? "↓" : "—"} {trend.label}
          </p>
        )}
        {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/admin/components/AdminKpiCard.tsx
git commit -m "feat(admin): add AdminKpiCard with trend indicator"
```

---

## Task 4: Frontend — AiPerformanceChart

**Files:**
- Create: `frontend/src/features/admin/components/AiPerformanceChart.tsx`

- [ ] **Step 1: Create component**

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import type { AdminAiStats } from "../types";

interface Props {
  ai: AdminAiStats;
  loading?: boolean;
}

function GaugeBar({ value, max, label }: { value: number; max: number; label: string }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{value}</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted">
        <div className="h-2 rounded-full bg-primary" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function MiniChart({ data, color }: { data: (number | null)[]; color: string }) {
  const valid = data.filter((v): v is number => v !== null);
  if (valid.length < 2) return <div className="h-16" />;
  const max = Math.max(...valid);
  const min = Math.min(...valid);
  const range = max - min || 1;
  const w = 100 / (valid.length - 1);

  const points = valid.map((v, i) => {
    const x = i * w;
    const y = 100 - ((v - min) / range) * 80 - 10;
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg viewBox="0 0 100 100" className="h-16 w-full" preserveAspectRatio="none">
      <polyline points={points} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

export function AiPerformanceChart({ ai, loading }: Props) {
  const t = useI18nStore((s) => s.t);

  if (loading) {
    return (
      <Card>
        <CardHeader><Skeleton className="h-5 w-48" /></CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </CardContent>
      </Card>
    );
  }

  const inferenceValues = ai.inference_trend.map((d) => d.avg_ms);
  const confidenceValues = ai.confidence_trend.map((d) => d.avg);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Performa AI", "AI Performance")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <p className="text-sm font-medium">{t("Waktu Inferensi", "Inference Time")}</p>
            <p className="text-2xl font-bold">{ai.avg_inference_ms}ms</p>
            <GaugeBar value={ai.avg_inference_ms} max={1000} label="avg" />
            <MiniChart data={inferenceValues} color="hsl(var(--primary))" />
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium">{t("Skor Kepercayaan", "Confidence Score")}</p>
            <p className="text-2xl font-bold">{(ai.avg_confidence * 100).toFixed(1)}%</p>
            <GaugeBar value={ai.avg_confidence * 100} max={100} label="avg" />
            <MiniChart data={confidenceValues} color="hsl(142, 76%, 36%)" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/admin/components/AiPerformanceChart.tsx
git commit -m "feat(admin): add AiPerformanceChart with gauges and mini charts"
```

---

## Task 5: Frontend — RecentAuditTable

**Files:**
- Create: `frontend/src/features/admin/components/RecentAuditTable.tsx`

- [ ] **Step 1: Create component**

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18nStore } from "@/lib/i18n/store";
import type { AdminAuditEntry } from "../types";

interface Props {
  entries: AdminAuditEntry[];
  loading?: boolean;
}

export function RecentAuditTable({ entries, loading }: Props) {
  const t = useI18nStore((s) => s.t);

  if (loading) {
    return (
      <Card>
        <CardHeader><Skeleton className="h-5 w-48" /></CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-8 w-full" />)}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("Aktivitas Terbaru", "Recent Activity")}</CardTitle>
      </CardHeader>
      <CardContent>
        {entries.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t("Belum ada aktivitas", "No activity yet")}</p>
        ) : (
          <div className="space-y-2">
            {entries.map((entry, i) => (
              <div key={i} className="flex items-center justify-between text-sm border-b pb-2 last:border-0">
                <span>
                  <span className="font-medium">User #{entry.user_id ?? "?"}</span>
                  {" "}{entry.action}{" "}
                  {entry.entity_type ?? ""}
                  {entry.entity_id ? ` #${entry.entity_id}` : ""}
                </span>
                <span className="text-xs text-muted-foreground">
                  {entry.created_at ? new Date(entry.created_at).toLocaleString("id-ID") : ""}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/admin/components/RecentAuditTable.tsx
git commit -m "feat(admin): add RecentAuditTable component"
```

---

## Task 6: Frontend — Rewrite AdminDashboardPage

**Files:**
- Modify: `frontend/src/features/admin/pages/AdminDashboardPage.tsx`

- [ ] **Step 1: Rewrite with Cloudflare layout**

Full file replacement — see Task 6 code in plan.

- [ ] **Step 2: Verify TypeScript**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

- [ ] **Step 3: Run frontend tests**

Run: `cd frontend && npx vitest run`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/admin/pages/AdminDashboardPage.tsx
git commit -m "feat(admin): rewrite AdminDashboardPage Cloudflare-style"
```

---

## Task 7: Full verification

- [ ] **Step 1: Backend** `cd backend && python -m pytest -v`
- [ ] **Step 2: Frontend** `cd frontend && npx vitest run`
- [ ] **Step 3: Build** `cd frontend && npx tsc -b && npx vite build`
