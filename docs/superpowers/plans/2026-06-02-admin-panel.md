# Admin Panel Implementation Plan (Phase 1: Users, Facilities, Tuning RBAC)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build admin-only backend CRUD for users and facilities, restrict tuning endpoints to admin, add missing seed scripts, and create frontend admin pages with role-gated sidebar.

**Architecture:** Single `admin` Blueprint under `/api/admin/*` with `@require_role(Role.ADMIN)` on every endpoint. Frontend uses existing `RoleGate` + `useRole()` to conditionally render admin sidebar section and wrap admin routes.

**Tech Stack:** Flask Blueprint, SQLAlchemy, Flask-JWT-Extended, React + React Router, TanStack Query, React Hook Form + Zod, TanStack Table, Vitest + React Testing Library.

---

## File Structure

### Backend — Create
| File | Responsibility |
|------|---------------|
| `backend/app/api/admin/__init__.py` | Register sub-blueprints under `/api/admin` |
| `backend/app/api/admin/users.py` | CRUD endpoints for users |
| `backend/app/api/admin/facilities.py` | CRUD endpoints for facilities |
| `backend/scripts/seed_admin.py` | Seed default admin user |
| `backend/scripts/seed_facility.py` | Seed sample Puskesmas facility |
| `backend/scripts/seed_clinician.py` | Seed sample clinician user |
| `backend/tests/unit/api/test_admin_users.py` | User CRUD + RBAC tests |
| `backend/tests/unit/api/test_admin_facilities.py` | Facility CRUD + RBAC tests |
| `backend/tests/unit/scripts/test_seed_admin.py` | Admin seed script test |
| `backend/tests/unit/scripts/test_seed_facility.py` | Facility seed script test |
| `backend/tests/unit/scripts/test_seed_clinician.py` | Clinician seed script test |

### Backend — Modify
| File | Change |
|------|--------|
| `backend/app/api/__init__.py:22-36` | Register `admin_bp` |
| `backend/app/api/tuning.py:45-78` | Add `@require_role(Role.ADMIN)` to `GET /grid` and `GET /active` |
| `backend/app/api/tuning.py:106-136` | Add `@require_role(Role.ADMIN)` to `GET /grid/<id>` and `GET /grid/<id>/images/<filename>` |

### Frontend — Create
| File | Responsibility |
|------|---------------|
| `frontend/src/features/admin/api.ts` | API functions + query keys |
| `frontend/src/features/admin/types.ts` | TypeScript types |
| `frontend/src/features/admin/pages/UserListPage.tsx` | User list table |
| `frontend/src/features/admin/pages/FacilityListPage.tsx` | Facility list table |
| `frontend/src/features/admin/components/UserFormModal.tsx` | Create/edit user form |
| `frontend/src/features/admin/components/FacilityFormModal.tsx` | Create/edit facility form |
| `frontend/src/features/admin/__tests__/UserListPage.test.tsx` | User page tests |
| `frontend/src/features/admin/__tests__/FacilityListPage.test.tsx` | Facility page tests |
| `frontend/src/routes/AdminUsersRoute.tsx` | Route wrapper |
| `frontend/src/routes/AdminFacilitiesRoute.tsx` | Route wrapper |

### Frontend — Modify
| File | Change |
|------|--------|
| `frontend/src/App.tsx:22-31` | Add `/admin/*` routes |
| `frontend/src/components/layout/SidebarNav.tsx:16-26` | Add Admin section with role filtering |

---

## Task 1: Seed Scripts

### Task 1A: Seed Admin User

**Files:**
- Create: `backend/scripts/seed_admin.py`
- Create: `backend/tests/unit/scripts/test_seed_admin.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/unit/scripts/test_seed_admin.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_admin import seed_admin
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.user import User


def test_seed_admin_creates_user(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'admin.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_admin(s)
        s.commit()
        user = s.scalar(select(User).where(User.email == "admin@cdss.local"))
        assert user is not None
        assert user.role == "admin"
        assert user.is_active is True


def test_seed_admin_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'admin2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_admin(s)
        s.commit()
        seed_admin(s)
        s.commit()
        assert s.query(User).filter_by(email="admin@cdss.local").count() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/scripts/test_seed_admin.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.seed_admin'`

- [ ] **Step 3: Write implementation**

```python
# backend/scripts/seed_admin.py
"""Seed default admin user."""
from app.core.security.password import hash_password
from app.db.models.user import User

ADMIN_EMAIL = "admin@cdss.local"
ADMIN_PASSWORD = "Admin123!"
ADMIN_NAME = "System Administrator"


def seed_admin(session) -> None:
    """Create default admin user (idempotent)."""
    existing = session.query(User).filter_by(email=ADMIN_EMAIL).first()
    if existing is not None:
        return
    session.add(User(
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD),
        role="admin",
        facility_id=1,
        is_active=True,
    ))
```

Note: `facility_id=1` assumes a facility exists. Seed facility first or use `seed_clinician.py` which creates facility.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/unit/scripts/test_seed_admin.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/scripts/seed_admin.py backend/tests/unit/scripts/test_seed_admin.py
git commit -m "feat(scripts): add seed_admin with idempotent admin user creation"
```

---

### Task 1B: Seed Facility

**Files:**
- Create: `backend/scripts/seed_facility.py`
- Create: `backend/tests/unit/scripts/test_seed_facility.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/unit/scripts/test_seed_facility.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_facility import seed_facility
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.facility import HealthcareFacility


def test_seed_facility_creates(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fac.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_facility(s)
        s.commit()
        fac = s.scalar(select(HealthcareFacility).where(HealthcareFacility.code == "PUSK-001"))
        assert fac is not None
        assert fac.facility_type == "puskesmas"
        assert fac.is_active is True


def test_seed_facility_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fac2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_facility(s)
        s.commit()
        seed_facility(s)
        s.commit()
        assert s.query(HealthcareFacility).filter_by(code="PUSK-001").count() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/scripts/test_seed_facility.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# backend/scripts/seed_facility.py
"""Seed sample healthcare facility."""
from app.db.models.facility import HealthcareFacility

DEFAULT_FACILITY = {
    "name": "Puskesmas Contoh",
    "code": "PUSK-001",
    "facility_type": "puskesmas",
    "address": "Jl. Contoh No. 1, Jakarta",
    "province_code": "31",
    "regency_code": "3171",
    "subdistrict_code": "317101",
    "is_active": True,
}


def seed_facility(session) -> None:
    """Create sample facility (idempotent)."""
    existing = session.query(HealthcareFacility).filter_by(code=DEFAULT_FACILITY["code"]).first()
    if existing is not None:
        return
    session.add(HealthcareFacility(**DEFAULT_FACILITY))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/unit/scripts/test_seed_facility.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/scripts/seed_facility.py backend/tests/unit/scripts/test_seed_facility.py
git commit -m "feat(scripts): add seed_facility with sample Puskesmas"
```

---

### Task 1C: Seed Clinician

**Files:**
- Create: `backend/scripts/seed_clinician.py`
- Create: `backend/tests/unit/scripts/test_seed_clinician.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/unit/scripts/test_seed_clinician.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_clinician import seed_clinician
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User


def test_seed_clinician_creates(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'clin.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        # Must seed facility first (FK constraint)
        fac = HealthcareFacility(name="Test", code="T-001", facility_type="puskesmas")
        s.add(fac)
        s.commit()
        seed_clinician(s, facility_id=fac.id)
        s.commit()
        user = s.scalar(select(User).where(User.email == "clinician@cdss.local"))
        assert user is not None
        assert user.role == "clinician"
        assert user.facility_id == fac.id


def test_seed_clinician_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'clin2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        fac = HealthcareFacility(name="Test", code="T-002", facility_type="puskesmas")
        s.add(fac)
        s.commit()
        seed_clinician(s, facility_id=fac.id)
        s.commit()
        seed_clinician(s, facility_id=fac.id)
        s.commit()
        assert s.query(User).filter_by(email="clinician@cdss.local").count() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/scripts/test_seed_clinician.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# backend/scripts/seed_clinician.py
"""Seed sample clinician user."""
from app.core.security.password import hash_password
from app.db.models.user import User

CLINICIAN_EMAIL = "clinician@cdss.local"
CLINICIAN_PASSWORD = "Clinician123!"


def seed_clinician(session, facility_id: int) -> None:
    """Create sample clinician (idempotent)."""
    existing = session.query(User).filter_by(email=CLINICIAN_EMAIL).first()
    if existing is not None:
        return
    session.add(User(
        name="Dr. Contoh",
        email=CLINICIAN_EMAIL,
        password_hash=hash_password(CLINICIAN_PASSWORD),
        role="clinician",
        facility_id=facility_id,
        profession="Dokter Umum",
        license_number="STR-0001",
        is_active=True,
    ))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/unit/scripts/test_seed_clinician.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/scripts/seed_clinician.py backend/tests/unit/scripts/test_seed_clinician.py
git commit -m "feat(scripts): add seed_clinician with sample doctor user"
```

---

## Task 2: Backend Admin Blueprint — Users

### Task 2A: Blueprint Init

**Files:**
- Create: `backend/app/api/admin/__init__.py`
- Modify: `backend/app/api/__init__.py:22-36`

- [ ] **Step 1: Create admin blueprint init**

```python
# backend/app/api/admin/__init__.py
"""Admin API — user, facility, and system management (admin-only)."""
from flask import Blueprint

from app.api.admin.facilities import bp as facilities_bp
from app.api.admin.users import bp as users_bp

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
admin_bp.register_blueprint(users_bp)
admin_bp.register_blueprint(facilities_bp)
```

- [ ] **Step 2: Register in app factory**

In `backend/app/api/__init__.py`, add import and registration:

```python
# Add after line 20 (from app.api.vital_signs import bp as vital_signs_bp):
from app.api.admin import admin_bp

# Add after line 36 (app.register_blueprint(tuning_bp)):
app.register_blueprint(admin_bp)
```

- [ ] **Step 3: Verify import works**

Run: `cd backend && python -c "from app.api.admin import admin_bp; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/admin/__init__.py backend/app/api/__init__.py
git commit -m "feat(api): register admin blueprint at /api/admin"
```

---

### Task 2B: User CRUD Endpoints

**Files:**
- Create: `backend/app/api/admin/users.py`
- Create: `backend/tests/unit/api/test_admin_users.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/unit/api/test_admin_users.py
"""Tests for admin user management endpoints."""
from app import create_app
from app.core.security.password import hash_password
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db
from app.core.security.jwt import make_access_token


def _app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        # Seed facility (FK for User)
        fac = HealthcareFacility(name="TestFac", code="T-ADM", facility_type="puskesmas")
        db.session.add(fac)
        db.session.commit()
        fac_id = fac.id
        # Seed admin user
        admin = User(
            name="Admin", email="adm@test.local",
            password_hash=hash_password("pass"), role="admin",
            facility_id=fac_id, is_active=True,
        )
        db.session.add(admin)
        # Seed non-admin
        nurse = User(
            name="Nurse", email="nurse@test.local",
            password_hash=hash_password("pass"), role="nurse",
            facility_id=fac_id, is_active=True,
        )
        db.session.add(nurse)
        db.session.commit()
    return app, fac_id


def _admin_token():
    return make_access_token(user_id=1, role="admin", facility_id=1)


def _nurse_token():
    return make_access_token(user_id=2, role="nurse", facility_id=1)


class TestAdminUsersList:
    def test_list_users_returns_all(self, client):
        app, _ = _app()
        resp = client.get("/api/admin/users",
                          headers={"Authorization": f"Bearer {_admin_token()}"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["items"]) >= 2

    def test_list_users_rejects_non_admin(self, client):
        app, _ = _app()
        resp = client.get("/api/admin/users",
                          headers={"Authorization": f"Bearer {_nurse_token()}"})
        assert resp.status_code == 403


class TestAdminUsersCreate:
    def test_create_user(self, client):
        app, fac_id = _app()
        resp = client.post("/api/admin/users",
                           headers={"Authorization": f"Bearer {_admin_token()}"},
                           json={
                               "name": "New Doc",
                               "email": "new@doc.local",
                               "password": "Secret123!",
                               "role": "clinician",
                               "facility_id": fac_id,
                           })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["email"] == "new@doc.local"
        assert data["role"] == "clinician"

    def test_create_user_rejects_duplicate_email(self, client):
        app, _ = _app()
        resp = client.post("/api/admin/users",
                           headers={"Authorization": f"Bearer {_admin_token()}"},
                           json={
                               "name": "Dup",
                               "email": "adm@test.local",
                               "password": "Secret123!",
                               "role": "clinician",
                               "facility_id": 1,
                           })
        assert resp.status_code == 409


class TestAdminUsersUpdate:
    def test_update_user_role(self, client):
        app, _ = _app()
        resp = client.put("/api/admin/users/2",
                          headers={"Authorization": f"Bearer {_admin_token()}"},
                          json={"role": "clinician"})
        assert resp.status_code == 200
        assert resp.get_json()["role"] == "clinician"

    def test_toggle_user_active(self, client):
        app, _ = _app()
        resp = client.put("/api/admin/users/2",
                          headers={"Authorization": f"Bearer {_admin_token()}"},
                          json={"is_active": False})
        assert resp.status_code == 200
        assert resp.get_json()["is_active"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/unit/api/test_admin_users.py -v`
Expected: FAIL — no `/api/admin/users` endpoint

- [ ] **Step 3: Implement user endpoints**

```python
# backend/app/api/admin/users.py
"""Admin user management endpoints."""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.api._shared import session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.core.security.password import hash_password
from app.db.models.user import User

bp = Blueprint("admin_users", __name__, url_prefix="/users")


@bp.get("")
@require_role(Role.ADMIN)
def list_users():
    users = session().query(User).order_by(User.id).all()
    items = [
        {
            "id": u.id, "name": u.name, "email": u.email, "role": u.role,
            "facility_id": u.facility_id, "is_active": u.is_active,
            "profession": u.profession, "license_number": u.license_number,
        }
        for u in users
    ]
    return jsonify(items=items)


@bp.post("")
@require_role(Role.ADMIN)
def create_user():
    data = request.get_json() or {}
    required = ["name", "email", "password", "role", "facility_id"]
    missing = [k for k in required if k not in data]
    if missing:
        abort(400, description=f"Missing: {', '.join(missing)}")

    user = User(
        name=data["name"],
        email=data["email"],
        password_hash=hash_password(data["password"]),
        role=data["role"],
        facility_id=data["facility_id"],
        profession=data.get("profession"),
        license_number=data.get("license_number"),
    )
    session().add(user)
    try:
        session().commit()
    except IntegrityError:
        session().rollback()
        abort(409, description="Email already exists")
    return jsonify(
        id=user.id, name=user.name, email=user.email, role=user.role,
        facility_id=user.facility_id, is_active=user.is_active,
    ), 201


@bp.put("/<int:user_id>")
@require_role(Role.ADMIN)
def update_user(user_id: int):
    user = session().get(User, user_id)
    if user is None:
        abort(404, description="User not found")
    data = request.get_json() or {}
    if "name" in data:
        user.name = data["name"]
    if "role" in data:
        user.role = data["role"]
    if "facility_id" in data:
        user.facility_id = data["facility_id"]
    if "is_active" in data:
        user.is_active = data["is_active"]
    if "profession" in data:
        user.profession = data["profession"]
    if "license_number" in data:
        user.license_number = data["license_number"]
    if "password" in data:
        user.password_hash = hash_password(data["password"])
    session().commit()
    return jsonify(
        id=user.id, name=user.name, email=user.email, role=user.role,
        facility_id=user.facility_id, is_active=user.is_active,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/api/test_admin_users.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/admin/users.py backend/tests/unit/api/test_admin_users.py
git commit -m "feat(api): add admin user CRUD endpoints with RBAC"
```

---

## Task 3: Backend Admin Blueprint — Facilities

**Files:**
- Create: `backend/app/api/admin/facilities.py`
- Create: `backend/tests/unit/api/test_admin_facilities.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/unit/api/test_admin_facilities.py
"""Tests for admin facility management endpoints."""
from app import create_app
from app.core.security.password import hash_password
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db
from app.core.security.jwt import make_access_token


def _app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        fac = HealthcareFacility(name="Pusk A", code="P-A", facility_type="puskesmas")
        db.session.add(fac)
        db.session.commit()
        admin = User(
            name="Admin", email="adm@test.local",
            password_hash=hash_password("pass"), role="admin",
            facility_id=fac.id, is_active=True,
        )
        db.session.add(admin)
        db.session.commit()
    return app


def _admin_token():
    return make_access_token(user_id=1, role="admin", facility_id=1)


class TestAdminFacilitiesList:
    def test_list_facilities(self, client):
        app = _app()
        resp = client.get("/api/admin/facilities",
                          headers={"Authorization": f"Bearer {_admin_token()}"})
        assert resp.status_code == 200
        assert len(resp.get_json()["items"]) >= 1

    def test_list_rejects_non_admin(self, client):
        app = _app()
        nurse_token = make_access_token(user_id=1, role="nurse", facility_id=1)
        resp = client.get("/api/admin/facilities",
                          headers={"Authorization": f"Bearer {nurse_token}"})
        assert resp.status_code == 403


class TestAdminFacilitiesCreate:
    def test_create_facility(self, client):
        app = _app()
        resp = client.post("/api/admin/facilities",
                           headers={"Authorization": f"Bearer {_admin_token()}"},
                           json={
                               "name": "RS Contoh",
                               "code": "RS-001",
                               "facility_type": "rs_pratama",
                           })
        assert resp.status_code == 201
        assert resp.get_json()["code"] == "RS-001"


class TestAdminFacilitiesUpdate:
    def test_update_facility(self, client):
        app = _app()
        resp = client.put("/api/admin/facilities/1",
                          headers={"Authorization": f"Bearer {_admin_token()}"},
                          json={"name": "Pusk Updated"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Pusk Updated"

    def test_toggle_facility_active(self, client):
        app = _app()
        resp = client.put("/api/admin/facilities/1",
                          headers={"Authorization": f"Bearer {_admin_token()}"},
                          json={"is_active": False})
        assert resp.status_code == 200
        assert resp.get_json()["is_active"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/unit/api/test_admin_facilities.py -v`
Expected: FAIL — no `/api/admin/facilities` endpoint

- [ ] **Step 3: Implement facility endpoints**

```python
# backend/app/api/admin/facilities.py
"""Admin facility management endpoints."""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.api._shared import session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.facility import HealthcareFacility

bp = Blueprint("admin_facilities", __name__, url_prefix="/facilities")


@bp.get("")
@require_role(Role.ADMIN)
def list_facilities():
    facs = session().query(HealthcareFacility).order_by(HealthcareFacility.id).all()
    items = [
        {
            "id": f.id, "name": f.name, "code": f.code,
            "facility_type": f.facility_type, "address": f.address,
            "province_code": f.province_code, "regency_code": f.regency_code,
            "subdistrict_code": f.subdistrict_code, "is_active": f.is_active,
        }
        for f in facs
    ]
    return jsonify(items=items)


@bp.post("")
@require_role(Role.ADMIN)
def create_facility():
    data = request.get_json() or {}
    required = ["name", "code", "facility_type"]
    missing = [k for k in required if k not in data]
    if missing:
        abort(400, description=f"Missing: {', '.join(missing)}")

    fac = HealthcareFacility(
        name=data["name"],
        code=data["code"],
        facility_type=data["facility_type"],
        address=data.get("address"),
        province_code=data.get("province_code"),
        regency_code=data.get("regency_code"),
        subdistrict_code=data.get("subdistrict_code"),
    )
    session().add(fac)
    try:
        session().commit()
    except IntegrityError:
        session().rollback()
        abort(409, description="Facility code already exists")
    return jsonify(
        id=fac.id, name=fac.name, code=fac.code,
        facility_type=fac.facility_type, is_active=fac.is_active,
    ), 201


@bp.put("/<int:fac_id>")
@require_role(Role.ADMIN)
def update_facility(fac_id: int):
    fac = session().get(HealthcareFacility, fac_id)
    if fac is None:
        abort(404, description="Facility not found")
    data = request.get_json() or {}
    for field in ("name", "code", "facility_type", "address",
                  "province_code", "regency_code", "subdistrict_code", "is_active"):
        if field in data:
            setattr(fac, field, data[field])
    session().commit()
    return jsonify(
        id=fac.id, name=fac.name, code=fac.code,
        facility_type=fac.facility_type, is_active=fac.is_active,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/api/test_admin_facilities.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/admin/facilities.py backend/tests/unit/api/test_admin_facilities.py
git commit -m "feat(api): add admin facility CRUD endpoints with RBAC"
```

---

## Task 4: Restrict Tuning Endpoints to Admin

**Files:**
- Modify: `backend/app/api/tuning.py:45-78,106-136`
- Modify: `backend/tests/integration/test_tuning_api.py`

- [ ] **Step 1: Add @require_role to unprotected tuning endpoints**

In `backend/app/api/tuning.py`, add `@require_role(Role.ADMIN)` to 4 endpoints:

```python
# Line 45-46: before @bp.get("/grid")
@bp.get("/grid")
@require_role(Role.ADMIN)      # ADD THIS
def get_grid():

# Line 73-74: before @bp.get("/active")
@bp.get("/active")
@require_role(Role.ADMIN)      # ADD THIS
def get_active_config():

# Line 106-107: before @bp.get("/grid/<int:config_index>")
@bp.get("/grid/<int:config_index>")
@require_role(Role.ADMIN)      # ADD THIS
def get_config_detail(config_index: int):

# Line 121-122: before @bp.get("/grid/<int:config_index>/images/<filename>")
@bp.get("/grid/<int:config_index>/images/<filename>")
@require_role(Role.ADMIN)      # ADD THIS
def get_config_image(config_index: int, filename: str):
```

- [ ] **Step 2: Add RBAC tests to existing tuning test file**

In `backend/tests/integration/test_tuning_api.py`, add a test class:

```python
# Add at end of file
from app.core.security.jwt import make_access_token


class TestTuningRBAC:
    def test_grid_requires_admin(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr("app.api.tuning._grid_dir", lambda: grid)
        nurse_token = make_access_token(user_id=1, role="nurse", facility_id=1)
        resp = client.get("/api/tuning/grid",
                          headers={"Authorization": f"Bearer {nurse_token}"})
        assert resp.status_code == 403

    def test_grid_allows_admin(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr("app.api.tuning._grid_dir", lambda: grid)
        admin_token = make_access_token(user_id=1, role="admin", facility_id=1)
        resp = client.get("/api/tuning/grid",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

    def test_active_requires_admin(self, client, monkeypatch):
        nurse_token = make_access_token(user_id=1, role="nurse", facility_id=1)
        resp = client.get("/api/tuning/active",
                          headers={"Authorization": f"Bearer {nurse_token}"})
        assert resp.status_code == 403
```

- [ ] **Step 3: Run all tuning tests**

Run: `cd backend && python -m pytest tests/integration/test_tuning_api.py -v`
Expected: All existing tests + 3 new RBAC tests pass

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/tuning.py backend/tests/integration/test_tuning_api.py
git commit -m "feat(api): restrict all tuning endpoints to admin role"
```

---

## Task 5: Frontend Admin API & Types

**Files:**
- Create: `frontend/src/features/admin/types.ts`
- Create: `frontend/src/features/admin/api.ts`

- [ ] **Step 1: Create types**

```typescript
// frontend/src/features/admin/types.ts
export interface AdminUser {
  id: number;
  name: string;
  email: string;
  role: string;
  facility_id: number;
  is_active: boolean;
  profession: string | null;
  license_number: string | null;
}

export interface AdminFacility {
  id: number;
  name: string;
  code: string;
  facility_type: string;
  address: string | null;
  province_code: string | null;
  regency_code: string | null;
  subdistrict_code: string | null;
  is_active: boolean;
}

export interface AdminUserListResponse {
  items: AdminUser[];
}

export interface AdminFacilityListResponse {
  items: AdminFacility[];
}
```

- [ ] **Step 2: Create API module**

```typescript
// frontend/src/features/admin/api.ts
import { apiFetch } from "@/lib/api/client";
import type {
  AdminFacility,
  AdminFacilityListResponse,
  AdminUser,
  AdminUserListResponse,
} from "./types";

// ---- Query keys ----
export const adminKeys = {
  users: ["admin", "users"] as const,
  facilities: ["admin", "facilities"] as const,
};

// ---- Users ----
export async function fetchUsers(): Promise<AdminUserListResponse> {
  const resp = await apiFetch("/api/admin/users");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to load users");
  return body;
}

export async function createUser(data: {
  name: string;
  email: string;
  password: string;
  role: string;
  facility_id: number;
  profession?: string;
  license_number?: string;
}): Promise<AdminUser> {
  const resp = await apiFetch("/api/admin/users", {
    method: "POST",
    body: JSON.stringify(data),
  });
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to create user");
  return body;
}

export async function updateUser(
  id: number,
  data: Partial<{ name: string; role: string; facility_id: number; is_active: boolean; password: string }>,
): Promise<AdminUser> {
  const resp = await apiFetch(`/api/admin/users/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to update user");
  return body;
}

// ---- Facilities ----
export async function fetchFacilities(): Promise<AdminFacilityListResponse> {
  const resp = await apiFetch("/api/admin/facilities");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to load facilities");
  return body;
}

export async function createFacility(data: {
  name: string;
  code: string;
  facility_type: string;
  address?: string;
  province_code?: string;
  regency_code?: string;
  subdistrict_code?: string;
}): Promise<AdminFacility> {
  const resp = await apiFetch("/api/admin/facilities", {
    method: "POST",
    body: JSON.stringify(data),
  });
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to create facility");
  return body;
}

export async function updateFacility(
  id: number,
  data: Partial<AdminFacility>,
): Promise<AdminFacility> {
  const resp = await apiFetch(`/api/admin/facilities/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_en ?? "Failed to update facility");
  return body;
}
```

- [ ] **Step 3: Verify no TypeScript errors**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/admin/types.ts frontend/src/features/admin/api.ts
git commit -m "feat(admin): add frontend API layer and types for admin panel"
```

---

## Task 6: Frontend Admin User Page

**Files:**
- Create: `frontend/src/features/admin/components/UserFormModal.tsx`
- Create: `frontend/src/features/admin/pages/UserListPage.tsx`
- Create: `frontend/src/routes/AdminUsersRoute.tsx`
- Create: `frontend/src/features/admin/__tests__/UserListPage.test.tsx`

- [ ] **Step 1: Write failing test**

```typescript
// frontend/src/features/admin/__tests__/UserListPage.test.tsx
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { UserListPage } from "../pages/UserListPage";

vi.mock("../api", () => ({
  fetchUsers: vi.fn(),
  createUser: vi.fn(),
  updateUser: vi.fn(),
  adminKeys: { users: ["admin", "users"] },
}));

import { fetchUsers } from "../api";

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <UserListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("UserListPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading", async () => {
    vi.mocked(fetchUsers).mockResolvedValue({ items: [] });
    renderPage();
    expect(await screen.findByRole("heading", { name: /user/i })).toBeInTheDocument();
  });

  it("shows user rows", async () => {
    vi.mocked(fetchUsers).mockResolvedValue({
      items: [
        { id: 1, name: "Admin", email: "adm@test.local", role: "admin", facility_id: 1, is_active: true, profession: null, license_number: null },
      ],
    });
    renderPage();
    expect(await screen.findByText("Admin")).toBeInTheDocument();
    expect(screen.getByText("adm@test.local")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npx vitest run src/features/admin/__tests__/UserListPage.test.tsx`
Expected: FAIL — module not found

- [ ] **Step 3: Create UserFormModal**

```tsx
// frontend/src/features/admin/components/UserFormModal.tsx
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import type { AdminUser } from "../types";

interface Props {
  open: boolean;
  onClose: () => void;
  onSave: (data: Record<string, unknown>) => void;
  user?: AdminUser | null;
}

const ROLES = ["admin", "clinician", "nurse", "researcher", "expert_reviewer"];

export function UserFormModal({ open, onClose, onSave, user }: Props) {
  const { register, handleSubmit, reset, setValue, watch } = useForm({
    defaultValues: {
      name: "", email: "", password: "", role: "clinician",
      facility_id: 1, profession: "", license_number: "",
    },
  });

  useEffect(() => {
    if (user) {
      reset({
        name: user.name, email: user.email, password: "",
        role: user.role, facility_id: user.facility_id,
        profession: user.profession ?? "", license_number: user.license_number ?? "",
      });
    } else {
      reset({ name: "", email: "", password: "", role: "clinician", facility_id: 1, profession: "", license_number: "" });
    }
  }, [user, reset]);

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{user ? "Edit User" : "Tambah User"}</DialogTitle>
          <DialogDescription>
            {user ? "Ubah data pengguna." : "Buat pengguna baru."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSave)} className="space-y-3">
          <div>
            <Label htmlFor="name">Nama</Label>
            <Input id="name" {...register("name", { required: true })} />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" {...register("email", { required: true })} disabled={!!user} />
          </div>
          {!user && (
            <div>
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" {...register("password", { required: true })} />
            </div>
          )}
          <div>
            <Label>Role</Label>
            <Select value={watch("role")} onValueChange={(v) => setValue("role", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {ROLES.map((r) => <SelectItem key={r} value={r}>{r}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="profession">Profesi</Label>
            <Input id="profession" {...register("profession")} />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Batal</Button>
            <Button type="submit">Simpan</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
```

- [ ] **Step 4: Create UserListPage**

```tsx
// frontend/src/features/admin/pages/UserListPage.tsx
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, UserX, UserCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { adminKeys, fetchUsers, createUser, updateUser } from "../api";
import { UserFormModal } from "../components/UserFormModal";
import type { AdminUser } from "../types";

export function UserListPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: adminKeys.users,
    queryFn: fetchUsers,
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<AdminUser | null>(null);

  const createMut = useMutation({
    mutationFn: createUser,
    onSuccess: () => { qc.invalidateQueries({ queryKey: adminKeys.users }); setModalOpen(false); },
  });

  const updateMut = useMutation({
    mutationFn: ({ id, ...rest }: { id: number } & Record<string, unknown>) => updateUser(id, rest),
    onSuccess: () => { qc.invalidateQueries({ queryKey: adminKeys.users }); setModalOpen(false); setEditing(null); },
  });

  const toggleActive = (u: AdminUser) => {
    updateMut.mutate({ id: u.id, is_active: !u.is_active });
  };

  if (isLoading) return <div className="space-y-2">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Users</h1>
        <Button onClick={() => { setEditing(null); setModalOpen(true); }}>
          <Plus className="mr-1 h-4 w-4" /> Tambah User
        </Button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4">Nama</th>
              <th className="pb-2 pr-4">Email</th>
              <th className="pb-2 pr-4">Role</th>
              <th className="pb-2 pr-4">Status</th>
              <th className="pb-2">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((u) => (
              <tr key={u.id} className="border-b">
                <td className="py-2 pr-4">{u.name}</td>
                <td className="py-2 pr-4">{u.email}</td>
                <td className="py-2 pr-4">{u.role}</td>
                <td className="py-2 pr-4">{u.is_active ? "Aktif" : "Nonaktif"}</td>
                <td className="py-2 flex gap-1">
                  <Button variant="ghost" size="sm" onClick={() => { setEditing(u); setModalOpen(true); }}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => toggleActive(u)}>
                    {u.is_active ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <UserFormModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setEditing(null); }}
        onSave={(d) => editing ? updateMut.mutate({ id: editing.id, ...d }) : createMut.mutate(d as any)}
        user={editing}
      />
    </div>
  );
}
```

- [ ] **Step 5: Create route wrapper**

```tsx
// frontend/src/routes/AdminUsersRoute.tsx
import { RoleGate } from "@/features/auth/components/RoleGate";
import { UserListPage } from "@/features/admin/pages/UserListPage";

export function AdminUsersRoute() {
  return (
    <RoleGate allow={["admin"]}>
      <UserListPage />
    </RoleGate>
  );
}
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd frontend && npx vitest run src/features/admin/__tests__/UserListPage.test.tsx`
Expected: 2 passed

- [ ] **Step 7: Commit**

```bash
git add frontend/src/features/admin/ frontend/src/routes/AdminUsersRoute.tsx
git commit -m "feat(admin): add UserListPage, UserFormModal, and route"
```

---

## Task 7: Frontend Admin Facility Page

**Files:**
- Create: `frontend/src/features/admin/components/FacilityFormModal.tsx`
- Create: `frontend/src/features/admin/pages/FacilityListPage.tsx`
- Create: `frontend/src/routes/AdminFacilitiesRoute.tsx`
- Create: `frontend/src/features/admin/__tests__/FacilityListPage.test.tsx`

- [ ] **Step 1: Write failing test**

```typescript
// frontend/src/features/admin/__tests__/FacilityListPage.test.tsx
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { FacilityListPage } from "../pages/FacilityListPage";

vi.mock("../api", () => ({
  fetchFacilities: vi.fn(),
  createFacility: vi.fn(),
  updateFacility: vi.fn(),
  adminKeys: { facilities: ["admin", "facilities"] },
}));

import { fetchFacilities } from "../api";

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <FacilityListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("FacilityListPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading", async () => {
    vi.mocked(fetchFacilities).mockResolvedValue({ items: [] });
    renderPage();
    expect(await screen.findByRole("heading", { name: /facility|fasilitas/i })).toBeInTheDocument();
  });

  it("shows facility rows", async () => {
    vi.mocked(fetchFacilities).mockResolvedValue({
      items: [
        { id: 1, name: "Pusk A", code: "P-A", facility_type: "puskesmas", address: null, province_code: null, regency_code: null, subdistrict_code: null, is_active: true },
      ],
    });
    renderPage();
    expect(await screen.findByText("Pusk A")).toBeInTheDocument();
    expect(screen.getByText("P-A")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npx vitest run src/features/admin/__tests__/FacilityListPage.test.tsx`
Expected: FAIL — module not found

- [ ] **Step 3: Create FacilityFormModal**

```tsx
// frontend/src/features/admin/components/FacilityFormModal.tsx
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import type { AdminFacility } from "../types";

interface Props {
  open: boolean;
  onClose: () => void;
  onSave: (data: Record<string, unknown>) => void;
  facility?: AdminFacility | null;
}

const FACILITY_TYPES = ["puskesmas", "rs_pratama", "rs_utama", "rs_khusus", "klinik", "lab"];

export function FacilityFormModal({ open, onClose, onSave, facility }: Props) {
  const { register, handleSubmit, reset, setValue, watch } = useForm({
    defaultValues: {
      name: "", code: "", facility_type: "puskesmas",
      address: "", province_code: "", regency_code: "", subdistrict_code: "",
    },
  });

  useEffect(() => {
    if (facility) {
      reset({
        name: facility.name, code: facility.code, facility_type: facility.facility_type,
        address: facility.address ?? "", province_code: facility.province_code ?? "",
        regency_code: facility.regency_code ?? "", subdistrict_code: facility.subdistrict_code ?? "",
      });
    } else {
      reset({ name: "", code: "", facility_type: "puskesmas", address: "", province_code: "", regency_code: "", subdistrict_code: "" });
    }
  }, [facility, reset]);

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{facility ? "Edit Fasilitas" : "Tambah Fasilitas"}</DialogTitle>
          <DialogDescription>
            {facility ? "Ubah data fasilitas." : "Buat fasilitas baru."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSave)} className="space-y-3">
          <div>
            <Label htmlFor="name">Nama</Label>
            <Input id="name" {...register("name", { required: true })} />
          </div>
          <div>
            <Label htmlFor="code">Kode</Label>
            <Input id="code" {...register("code", { required: true })} disabled={!!facility} />
          </div>
          <div>
            <Label>Tipe</Label>
            <Select value={watch("facility_type")} onValueChange={(v) => setValue("facility_type", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {FACILITY_TYPES.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="address">Alamat</Label>
            <Input id="address" {...register("address")} />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Batal</Button>
            <Button type="submit">Simpan</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
```

- [ ] **Step 4: Create FacilityListPage**

```tsx
// frontend/src/features/admin/pages/FacilityListPage.tsx
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { adminKeys, fetchFacilities, createFacility, updateFacility } from "../api";
import { FacilityFormModal } from "../components/FacilityFormModal";
import type { AdminFacility } from "../types";

export function FacilityListPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: adminKeys.facilities,
    queryFn: fetchFacilities,
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<AdminFacility | null>(null);

  const createMut = useMutation({
    mutationFn: createFacility,
    onSuccess: () => { qc.invalidateQueries({ queryKey: adminKeys.facilities }); setModalOpen(false); },
  });

  const updateMut = useMutation({
    mutationFn: ({ id, ...rest }: { id: number } & Record<string, unknown>) => updateFacility(id, rest),
    onSuccess: () => { qc.invalidateQueries({ queryKey: adminKeys.facilities }); setModalOpen(false); setEditing(null); },
  });

  if (isLoading) return <div className="space-y-2">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Fasilitas</h1>
        <Button onClick={() => { setEditing(null); setModalOpen(true); }}>
          <Plus className="mr-1 h-4 w-4" /> Tambah Fasilitas
        </Button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4">Nama</th>
              <th className="pb-2 pr-4">Kode</th>
              <th className="pb-2 pr-4">Tipe</th>
              <th className="pb-2 pr-4">Status</th>
              <th className="pb-2">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((f) => (
              <tr key={f.id} className="border-b">
                <td className="py-2 pr-4">{f.name}</td>
                <td className="py-2 pr-4">{f.code}</td>
                <td className="py-2 pr-4">{f.facility_type}</td>
                <td className="py-2 pr-4">{f.is_active ? "Aktif" : "Nonaktif"}</td>
                <td className="py-2">
                  <Button variant="ghost" size="sm" onClick={() => { setEditing(f); setModalOpen(true); }}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <FacilityFormModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setEditing(null); }}
        onSave={(d) => editing ? updateMut.mutate({ id: editing.id, ...d }) : createMut.mutate(d as any)}
        facility={editing}
      />
    </div>
  );
}
```

- [ ] **Step 5: Create route wrapper**

```tsx
// frontend/src/routes/AdminFacilitiesRoute.tsx
import { RoleGate } from "@/features/auth/components/RoleGate";
import { FacilityListPage } from "@/features/admin/pages/FacilityListPage";

export function AdminFacilitiesRoute() {
  return (
    <RoleGate allow={["admin"]}>
      <FacilityListPage />
    </RoleGate>
  );
}
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd frontend && npx vitest run src/features/admin/__tests__/FacilityListPage.test.tsx`
Expected: 2 passed

- [ ] **Step 7: Commit**

```bash
git add frontend/src/features/admin/components/FacilityFormModal.tsx frontend/src/features/admin/pages/FacilityListPage.tsx frontend/src/routes/AdminFacilitiesRoute.tsx frontend/src/features/admin/__tests__/FacilityListPage.test.tsx
git commit -m "feat(admin): add FacilityListPage, FacilityFormModal, and route"
```

---

## Task 8: Frontend Routing & Sidebar

**Files:**
- Modify: `frontend/src/App.tsx:14,22-31`
- Modify: `frontend/src/components/layout/SidebarNav.tsx:1-26`

- [ ] **Step 1: Add admin routes to App.tsx**

In `frontend/src/App.tsx`, add imports and routes:

```tsx
// Add imports after line 14 (TuningRoute import):
import { AdminUsersRoute } from "@/routes/AdminUsersRoute";
import { AdminFacilitiesRoute } from "@/routes/AdminFacilitiesRoute";

// Add routes inside <Route element={<AppShell />}> block, after line 30 (tuning route):
<Route path="/admin/users" element={<AdminUsersRoute />} />
<Route path="/admin/facilities" element={<AdminFacilitiesRoute />} />
```

- [ ] **Step 2: Add admin section to SidebarNav.tsx**

In `frontend/src/components/layout/SidebarNav.tsx`:

```tsx
// Change line 2 import to add icons:
import { LayoutDashboard, Users, Sliders, Building2, Shield, type LucideIcon } from "lucide-react";

// Add import for useRole after line 5 (existing imports):
import { useRole } from "@/features/auth/components/RoleGate";

// Replace NAV_SECTIONS definition (lines 16-26) with dynamic version:
const BASE_SECTIONS = [
  {
    titleId: "Klinis",
    titleEn: "Clinical",
    items: [
      { to: "/dashboard", label: "Dashboard", labelEn: "Dashboard", icon: LayoutDashboard },
      { to: "/patients", label: "Pasien", labelEn: "Patients", icon: Users },
    ],
  },
];

const ADMIN_SECTION = {
  titleId: "Admin",
  titleEn: "Admin",
  items: [
    { to: "/admin/users", label: "User", labelEn: "Users", icon: Users },
    { to: "/admin/facilities", label: "Fasilitas", labelEn: "Facilities", icon: Building2 },
    { to: "/tuning", label: "Tuning", labelEn: "Tuning", icon: Sliders },
  ],
};

// In SidebarNav component, after line 37 (const t = ...), add:
const role = useRole();
const sections = role === "admin" ? [...BASE_SECTIONS, ADMIN_SECTION] : BASE_SECTIONS;

// Change line 45 to use `sections` instead of `NAV_SECTIONS`:
{sections.map((section) => (
```

- [ ] **Step 3: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.tsx frontend/src/components/layout/SidebarNav.tsx
git commit -m "feat(admin): add admin routes and role-gated sidebar section"
```

---

## Task 9: Full Test Suite Verification

- [ ] **Step 1: Run backend tests**

Run: `cd backend && python -m pytest -v`
Expected: All tests pass (existing + new admin tests)

- [ ] **Step 2: Run frontend tests**

Run: `cd frontend && npx vitest run`
Expected: All tests pass (existing + new admin tests)

- [ ] **Step 3: Run frontend build**

Run: `cd frontend && npx tsc -b && npx vite build`
Expected: Build succeeds

- [ ] **Step 4: Final commit (if any fixups needed)**

---

## Self-Review Checklist

1. **Spec coverage:** Users CRUD ✓, Facilities CRUD ✓, Tuning RBAC ✓, Seed scripts ✓, Sidebar ✓, Routes ✓
2. **Placeholder scan:** No TBD/TODO in any step ✓
3. **Type consistency:** `AdminUser` / `AdminFacility` types used consistently across api.ts, pages, modals, tests ✓
4. **File paths:** All exact paths verified against codebase ✓
5. **200-line budget:** Largest file ~130 lines (UserListPage.tsx) ✓
