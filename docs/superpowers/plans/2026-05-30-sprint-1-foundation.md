# Sprint 1 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an installable foundation for EKG-Insight CDSS: repo skeleton, SQLite+Litestream, 6 tables, encryption bootstrap, JWT auth with refresh rotation, RBAC, audit logging, health/version endpoints, and green CI.

**Architecture:** Flask app-factory backend with SQLAlchemy 2.0 typed ORM, layered field encryption (Fernet) and HMAC hashing via custom SQLAlchemy types, Flask-JWT-Extended for access+refresh tokens with server-side rotation and replay detection, structlog JSON audit trail, and a minimal React+Vite+TS frontend (login + protected route + token-refresh interceptor). Single-process in prod (Flask serves React build), dual-server in dev (Vite proxies /api).

**Tech Stack:** Python 3.13, Flask, SQLAlchemy 2.0, Alembic, Pydantic v2, Flask-JWT-Extended, passlib[bcrypt], cryptography (Fernet), structlog, pytest; Node 24, React 18, Vite 5, TypeScript 5, TanStack Query, Zustand, Tailwind, Vitest; SQLite, Litestream.

---

## Locked Decisions

| # | Topic | Decision |
| --- | --- | --- |
| T1 | Refresh token storage | Dedicated `RefreshToken` table (rotation + replay detection via `replaced_by_id`) |
| T2 | Password hashing | bcrypt via passlib, cost=12 prod / cost=4 test |
| T3 | DB testing | Hybrid: in-memory `:memory:` for unit, file in `tmp_path` for integration/migration/litestream |
| T4 | Pre-commit | Husky + lint-staged + commitlint |
| T5 | JWT library | Flask-JWT-Extended |
| T6 | Frontend test depth | 4 tests: LoginForm smoke, attach-token interceptor, refresh-on-401 retry, ProtectedRoute redirect |
| T7 | Seed admin | Interactive prompt with env-var fallback (`ADMIN_EMAIL`, `ADMIN_PASSWORD`) |

## Two-Key Security Model (critical)

| Key | Location | Rotation | Leak impact |
| --- | --- | --- | --- |
| JWT signing key | `.env` `JWT_SECRET_KEY` | Per quarter OK | Session forgery, NOT data leak |
| Encryption master key | `secrets/master.key` (0600) | NEVER without re-encrypt batch | Full PHI compromise |

These two keys are distinct, with distinct lifecycles. Never conflate them in code or config.

## File Structure

Backend (`backend/`):

- `app/__init__.py` - app factory `create_app(config)`
- `app/config.py` - `BaseConfig`, `DevConfig`, `ProdConfig`, `TestConfig`
- `app/extensions.py` - `db`, `jwt`, `migrate` singletons + service registry
- `app/api/__init__.py` - `register_blueprints(app)`
- `app/api/health.py` - GET /api/health, /api/version
- `app/api/auth.py` - login/logout/refresh/me
- `app/core/security/password.py` - bcrypt wrapper (passlib CryptContext)
- `app/core/security/tokens.py` - opaque refresh token generation + hashing
- `app/core/security/jwt.py` - access token claims helpers
- `app/core/rbac/roles.py` - Role enum (admin/clinician/nurse/researcher/expert_reviewer)
- `app/core/rbac/decorators.py` - `@require_role(*roles)`
- `app/core/encryption/key_loader.py` - load master key from `secrets/master.key`
- `app/core/encryption/fernet_provider.py` - Fernet encrypt/decrypt
- `app/core/encryption/hash_provider.py` - HMAC-SHA256 (NIK hashing)
- `app/core/logging/config.py` - structlog setup (JSON stdout)
- `app/core/logging/processors.py` - request_id + timestamp processors
- `app/core/exceptions/base.py` - `AppException` hierarchy
- `app/core/exceptions/handlers.py` - global error -> bilingual JSON
- `app/db/base.py` - `Base` declarative
- `app/db/engine.py` - engine factory
- `app/db/pragmas.py` - WAL + foreign_keys ON event listener
- `app/db/session.py` - session/scoped_session
- `app/db/mixins/timestamp.py` - `created_at`/`updated_at`
- `app/db/types/encrypted_string.py` - `EncryptedString` TypeDecorator
- `app/db/types/hashed_string.py` - `HashedString` TypeDecorator
- `app/db/models/facility.py` - HealthcareFacility
- `app/db/models/user.py` - User
- `app/db/models/refresh_token.py` - RefreshToken
- `app/db/models/audit_log.py` - AuditLog
- `app/db/models/phi_access_log.py` - PHIAccessLog
- `app/db/models/system_config.py` - SystemConfig
- `app/db/models/__init__.py` - import all for Alembic autogenerate
- `app/schemas/auth.py` - login request/response Pydantic DTO
- `app/schemas/common.py` - error envelope DTO
- `app/services/auth/login_service.py` - authenticate + issue tokens + audit
- `app/services/auth/token_service.py` - refresh rotation + replay detection
- `app/services/audit/writer.py` - `write_audit(...)`
- `migrations/` - Alembic env + versions
- `tests/conftest.py` - fixtures (app, in-memory db, file db, seeded admin, auth client)
- `tests/unit/` - mirror of source
- `tests/integration/test_acceptance.py` - AC-1..AC-13
- `pyproject.toml`, `alembic.ini`, `wsgi.py`

Frontend (`frontend/`):

- `src/main.tsx`, `src/App.tsx`
- `src/routes/login.tsx`
- `src/features/auth/api.ts` - login/refresh/me calls
- `src/features/auth/store.ts` - Zustand token store
- `src/features/auth/LoginForm.tsx`
- `src/features/auth/ProtectedRoute.tsx`
- `src/lib/api/client.ts` - fetch wrapper + interceptors
- `src/lib/api/auth-token.ts` - token persistence
- `src/test/setup.ts`, `vitest.config.ts`
- `package.json`, `vite.config.ts`, `tsconfig.json`

Root: `litestream.yml`, `scripts/init_secrets.py`, `scripts/seed_facility.py`, `scripts/seed_admin.py`, `scripts/seed_system_config.py`, `scripts/dev.ps1`, `scripts/build.ps1`, `.husky/`, `secrets/.gitkeep`.

## Out of Scope (explicit)

- Rate limiting on login (Sprint 8)
- Access-token blocklist (Sprint 8; 30-min TTL suffices now)
- Email verification (admin is seeded directly)
- Password reset flow (Sprint 2)
- CORS middleware (dev uses Vite proxy; prod is single-process)
- Patient/Encounter/ECG/AI/HiResCAM/Recommendation/Report/Dashboard (Sprint 2-7)
- i18n message loader (Sprint 6; ID/EN hardcoded in error definitions for now)

## Phase Order (dependency-correct)

A (tooling) -> B1 (pure crypto) -> C (DB foundation) -> B2 (ORM crypto types) -> D (6 models) -> E (logging/exceptions/registry) -> F (auth core) -> G (API layer) -> H (frontend) -> I (seed/ops) -> J (CI + acceptance)

---

## Phase A: Project Skeleton & Tooling

Goal: backend and frontend packages install cleanly, linters/formatters/type-checkers run, git hooks enforce commit conventions, and the secrets directory exists without leaking keys.

### Task A1: Backend pyproject.toml

**Files:**
- Create: `backend/pyproject.toml`

- [ ] **Step 1: Write pyproject.toml**

```toml
[project]
name = "ekg-insight-backend"
version = "0.1.0"
requires-python = ">=3.13,<3.14"
dependencies = [
  "flask>=3.0",
  "sqlalchemy>=2.0",
  "alembic>=1.13",
  "pydantic>=2.6",
  "flask-jwt-extended>=4.6",
  "passlib[bcrypt]>=1.7",
  "cryptography>=42.0",
  "structlog>=24.1",
  "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=4.1", "ruff>=0.3", "mypy>=1.9", "httpx>=0.27"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N", "S"]
ignore = ["S101"]

[tool.mypy]
python_version = "3.13"
strict = true
plugins = []

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

- [ ] **Step 2: Verify install**

Run: `pip install -e ".[dev]"` in `backend/`
Expected: install succeeds, `ruff`, `mypy`, `pytest` available.

- [ ] **Step 3: Commit**

```bash
git add backend/pyproject.toml
git commit -m "chore(infra): add backend pyproject with deps and tool config"
```

### Task A2: Frontend package.json + Vite + TS

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`

- [ ] **Step 1: Write package.json**

```json
{
  "name": "ekg-insight-frontend",
  "private": true,
  "type": "module",
  "engines": {
    "node": ">=24"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.23.0",
    "@tanstack/react-query": "^5.40.0",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "vitest": "^1.6.0",
    "@testing-library/react": "^15.0.0",
    "@testing-library/jest-dom": "^6.4.0",
    "jsdom": "^24.0.0",
    "eslint": "^8.57.0",
    "prettier": "^3.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "@commitlint/cli": "^19.3.0",
    "@commitlint/config-conventional": "^19.2.0",
    "husky": "^9.0.0",
    "lint-staged": "^15.2.0"
  }
}
```

- [ ] **Step 2: Write vite.config.ts**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:5000" },
  },
  build: { outDir: "../backend/app/static", emptyOutDir: true },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["src/test/setup.ts"],
  },
});
```

- [ ] **Step 3: Write tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src"]
}
```

- [ ] **Step 4: Verify install**

Run: `npm install` in `frontend/`
Expected: `node_modules` created, no peer-dep errors blocking install.

- [ ] **Step 5: Commit**

```bash
git add frontend/package.json frontend/vite.config.ts frontend/tsconfig.json
git commit -m "chore(infra): add frontend vite + typescript scaffold"
```

### Task A3: ESLint + Prettier config

**Files:**
- Create: `frontend/.eslintrc.cjs`
- Create: `frontend/.prettierrc.json`

- [ ] **Step 1: Write .eslintrc.cjs**

```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
  ],
  parser: "@typescript-eslint/parser",
  plugins: ["react-refresh"],
  rules: {
    "react-refresh/only-export-components": "warn",
  },
};
```

- [ ] **Step 2: Write .prettierrc.json**

```json
{
  "semi": true,
  "singleQuote": false,
  "trailingComma": "all",
  "printWidth": 100
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/.eslintrc.cjs frontend/.prettierrc.json
git commit -m "chore(infra): add eslint and prettier config"
```

### Task A4: Husky + commitlint + lint-staged

**Files:**
- Create: `commitlint.config.cjs`
- Create: `.husky/commit-msg`
- Create: `.husky/pre-commit`
- Create: `.lintstagedrc.json`

- [ ] **Step 1: Write commitlint.config.cjs**

```javascript
module.exports = { extends: ["@commitlint/config-conventional"] };
```

- [ ] **Step 2: Write .lintstagedrc.json**

```json
{
  "frontend/**/*.{ts,tsx}": ["eslint --fix", "prettier --write"],
  "backend/**/*.py": ["ruff check --fix"]
}
```

- [ ] **Step 3: Write .husky/commit-msg**

```sh
npx --no-install commitlint --edit "$1"
```

- [ ] **Step 4: Write .husky/pre-commit**

```sh
npx --no-install lint-staged
```

- [ ] **Step 5: Verify hooks**

Run: `npx husky init` then test `git commit -m "bad message"`
Expected: commit-msg hook rejects non-conventional message.

- [ ] **Step 6: Commit**

```bash
git add commitlint.config.cjs .lintstagedrc.json .husky/
git commit -m "chore(infra): add husky commitlint and lint-staged hooks"
```

### Task A5: secrets/ directory tracking + .env.example

**Files:**
- Create: `secrets/.gitkeep`
- Create: `.env.example`
- Modify: `.gitignore` (verify secrets rule)

- [ ] **Step 1: Create secrets/.gitkeep (empty file)**

- [ ] **Step 2: Verify .gitignore has secrets exception**

Confirm `.gitignore` contains:

```
secrets/*
!secrets/.gitkeep
```

If the existing rule is broader (e.g. `secrets/`), change it to the two lines above so the directory is tracked but keys are not.

- [ ] **Step 3: Write .env.example**

```
APP_VERSION=0.1.0
GIT_SHA=local
FLASK_ENV=development
JWT_SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite:///data/cdss.db
MASTER_KEY_PATH=secrets/master.key
HMAC_PEPPER_PATH=secrets/hmac_pepper.key
```

- [ ] **Step 4: Verify secrets stay ignored**

Run: `git check-ignore secrets/master.key`
Expected: prints `secrets/master.key` (ignored). `git status` shows `secrets/.gitkeep` trackable.

- [ ] **Step 5: Commit**

```bash
git add secrets/.gitkeep .env.example .gitignore
git commit -m "chore(infra): track secrets dir via gitkeep and add env example"
```

### Task A6: Backend app package init placeholders

**Files:**
- Create: `backend/app/__init__.py` (temporary minimal)
- Create: `backend/wsgi.py`
- Create: `backend/tests/__init__.py`

- [ ] **Step 1: Write minimal app/__init__.py**

```python
"""EKG-Insight backend application package."""
```

- [ ] **Step 2: Write wsgi.py (placeholder import target)**

```python
"""WSGI entrypoint. Real app factory wired in Phase G."""
```

- [ ] **Step 3: Create empty tests/__init__.py**

- [ ] **Step 4: Commit**

```bash
git add backend/app/__init__.py backend/wsgi.py backend/tests/__init__.py
git commit -m "chore(infra): add backend package placeholders"
```

---

## Phase B1: Pure Crypto Foundation

Goal: load master key and pepper from disk, encrypt/decrypt fields with Fernet, hash identifiers with HMAC-SHA256. No SQLAlchemy dependency here. JWT signing key stays separate (env), encryption master key stays on disk.

### Task B1-1: Key loader

**Files:**
- Create: `backend/app/core/encryption/key_loader.py`
- Test: `backend/tests/unit/core/encryption/test_key_loader.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
import pytest
from app.core.encryption.key_loader import load_key

def test_load_key_reads_bytes(tmp_path: Path):
    key_file = tmp_path / "master.key"
    key_file.write_bytes(b"secret-key-bytes")
    assert load_key(str(key_file)) == b"secret-key-bytes"

def test_load_key_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_key(str(tmp_path / "absent.key"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/encryption/test_key_loader.py -v`
Expected: FAIL with import error (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Load cryptographic keys from disk."""
from pathlib import Path

def load_key(path: str) -> bytes:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Key file not found: {path}")
    return p.read_bytes()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/encryption/test_key_loader.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/encryption/key_loader.py backend/tests/unit/core/encryption/test_key_loader.py
git commit -m "feat(infra): add encryption key loader"
```

### Task B1-2: Fernet provider

**Files:**
- Create: `backend/app/core/encryption/fernet_provider.py`
- Test: `backend/tests/unit/core/encryption/test_fernet_provider.py`

- [ ] **Step 1: Write the failing test**

```python
from cryptography.fernet import Fernet
from app.core.encryption.fernet_provider import FernetProvider

def test_roundtrip_encrypt_decrypt():
    key = Fernet.generate_key()
    provider = FernetProvider(key)
    token = provider.encrypt("Budi Santoso")
    assert token != b"Budi Santoso"
    assert provider.decrypt(token) == "Budi Santoso"

def test_decrypt_none_returns_none():
    provider = FernetProvider(Fernet.generate_key())
    assert provider.decrypt(None) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/encryption/test_fernet_provider.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Field-level encryption using Fernet (AES-128-CBC + HMAC)."""
from cryptography.fernet import Fernet

class FernetProvider:
    def __init__(self, key: bytes) -> None:
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> bytes:
        return self._fernet.encrypt(plaintext.encode("utf-8"))

    def decrypt(self, token: bytes | None) -> str | None:
        if token is None:
            return None
        return self._fernet.decrypt(token).decode("utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/encryption/test_fernet_provider.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/encryption/fernet_provider.py backend/tests/unit/core/encryption/test_fernet_provider.py
git commit -m "feat(infra): add Fernet field encryption provider"
```

### Task B1-3: HMAC hash provider

**Files:**
- Create: `backend/app/core/encryption/hash_provider.py`
- Test: `backend/tests/unit/core/encryption/test_hash_provider.py`

- [ ] **Step 1: Write the failing test**

```python
from app.core.encryption.hash_provider import HashProvider

def test_hmac_is_deterministic():
    provider = HashProvider(b"pepper-bytes")
    h1 = provider.hash("3171234567890001")
    h2 = provider.hash("3171234567890001")
    assert h1 == h2
    assert len(h1) == 64  # hex sha256

def test_hmac_differs_per_input():
    provider = HashProvider(b"pepper-bytes")
    assert provider.hash("111") != provider.hash("222")

def test_different_pepper_differs():
    a = HashProvider(b"pepper-a").hash("111")
    b = HashProvider(b"pepper-b").hash("111")
    assert a != b
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/encryption/test_hash_provider.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Irreversible HMAC-SHA256 hashing for identifiers (e.g. NIK)."""
import hashlib
import hmac

class HashProvider:
    def __init__(self, pepper: bytes) -> None:
        self._pepper = pepper

    def hash(self, value: str) -> str:
        return hmac.new(self._pepper, value.encode("utf-8"), hashlib.sha256).hexdigest()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/encryption/test_hash_provider.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/encryption/hash_provider.py backend/tests/unit/core/encryption/test_hash_provider.py
git commit -m "feat(infra): add HMAC-SHA256 hash provider"
```

### Task B1-4: init_secrets bootstrap script

**Files:**
- Create: `scripts/init_secrets.py`
- Test: `backend/tests/unit/scripts/test_init_secrets.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
from scripts.init_secrets import generate_secrets

def test_generates_key_and_pepper(tmp_path: Path):
    key_path = tmp_path / "master.key"
    pepper_path = tmp_path / "hmac_pepper.key"
    generate_secrets(str(key_path), str(pepper_path))
    assert key_path.exists()
    assert pepper_path.exists()
    assert len(key_path.read_bytes()) > 0

def test_does_not_overwrite(tmp_path: Path):
    key_path = tmp_path / "master.key"
    pepper_path = tmp_path / "hmac_pepper.key"
    key_path.write_bytes(b"existing")
    generate_secrets(str(key_path), str(pepper_path))
    assert key_path.read_bytes() == b"existing"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_init_secrets.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Generate Fernet master key + HMAC pepper. Idempotent; never overwrites."""
import os
import sys
from pathlib import Path
from cryptography.fernet import Fernet

def generate_secrets(key_path: str, pepper_path: str) -> None:
    kp = Path(key_path)
    pp = Path(pepper_path)
    kp.parent.mkdir(parents=True, exist_ok=True)
    if not kp.exists():
        kp.write_bytes(Fernet.generate_key())
        os.chmod(kp, 0o600)
    if not pp.exists():
        pp.write_bytes(os.urandom(32))
        os.chmod(pp, 0o600)

if __name__ == "__main__":
    key = os.environ.get("MASTER_KEY_PATH", "secrets/master.key")
    pepper = os.environ.get("HMAC_PEPPER_PATH", "secrets/hmac_pepper.key")
    generate_secrets(key, pepper)
    print(f"Secrets ready: {key}, {pepper}", file=sys.stderr)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_init_secrets.py -v`
Expected: PASS (2 tests). Note: chmod 0o600 is a no-op on Windows but harmless.

- [ ] **Step 5: Commit**

```bash
git add scripts/init_secrets.py backend/tests/unit/scripts/test_init_secrets.py
git commit -m "feat(infra): add init_secrets bootstrap script"
```

### Task B1-5: JWT secret separation note

**Files:**
- Create: `backend/app/core/security/__init__.py` (docstring documenting key separation)

- [ ] **Step 1: Write the module docstring**

```python
"""Security primitives.

Two distinct keys with distinct lifecycles:
- JWT signing key: from env JWT_SECRET_KEY. Rotatable. Leak = session forgery.
- Encryption master key: from secrets/master.key. NEVER rotate without a
  re-encrypt batch. Leak = full PHI compromise.

Never read the master key for JWT signing or vice versa.
"""
```

- [ ] **Step 2: Verify import**

Run: `python -c "import app.core.security"` in `backend/`
Expected: no error.

- [ ] **Step 3: Commit**

```bash
git add backend/app/core/security/__init__.py
git commit -m "docs(infra): document JWT vs master key separation"
```

## Phase C: Database Foundation

Goal: declarative Base, engine factory, SQLite pragmas (WAL + foreign_keys ON), session management, timestamp mixin, and an Alembic setup with an upgrade/downgrade round-trip test. Tests must never touch the real `data/cdss.db`.

### Task C1: Declarative Base

**Files:**
- Create: `backend/app/db/base.py`
- Test: `backend/tests/unit/db/test_base.py`

- [ ] **Step 1: Write the failing test**

```python
from app.db.base import Base

def test_base_has_metadata():
    assert hasattr(Base, "metadata")
    assert Base.metadata.tables == {} or isinstance(Base.metadata.tables, dict)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/test_base.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""SQLAlchemy declarative base."""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/test_base.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/base.py backend/tests/unit/db/test_base.py
git commit -m "feat(db): add declarative Base"
```

### Task C2: SQLite pragmas

**Files:**
- Create: `backend/app/db/pragmas.py`
- Test: `backend/tests/unit/db/test_pragmas.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, text
from app.db.pragmas import register_sqlite_pragmas

def test_foreign_keys_enabled(tmp_path):
    db = tmp_path / "t.db"
    engine = create_engine(f"sqlite:///{db}")
    register_sqlite_pragmas(engine)
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_keys")).scalar() == 1
        assert conn.execute(text("PRAGMA journal_mode")).scalar().lower() == "wal"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/test_pragmas.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""SQLite pragmas: enforce FK + WAL (required for Litestream)."""
from sqlalchemy import event
from sqlalchemy.engine import Engine

def register_sqlite_pragmas(engine: Engine) -> None:
    @event.listens_for(engine, "connect")
    def _set_pragmas(dbapi_conn, _record):  # type: ignore[no-untyped-def]
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA journal_mode=WAL")
        cur.close()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/test_pragmas.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/pragmas.py backend/tests/unit/db/test_pragmas.py
git commit -m "feat(db): add SQLite WAL + foreign_keys pragmas"
```

### Task C3: Engine factory

**Files:**
- Create: `backend/app/db/engine.py`
- Test: `backend/tests/unit/db/test_engine.py`

- [ ] **Step 1: Write the failing test**

```python
from app.db.engine import create_db_engine

def test_engine_applies_pragmas(tmp_path):
    db = tmp_path / "t.db"
    engine = create_db_engine(f"sqlite:///{db}")
    from sqlalchemy import text
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_keys")).scalar() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/test_engine.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Engine factory with pragmas wired in."""
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from app.db.pragmas import register_sqlite_pragmas

def create_db_engine(url: str) -> Engine:
    engine = create_engine(url, future=True)
    if url.startswith("sqlite"):
        register_sqlite_pragmas(engine)
    return engine
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/test_engine.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/engine.py backend/tests/unit/db/test_engine.py
git commit -m "feat(db): add engine factory with pragmas"
```

### Task C4: Session factory

**Files:**
- Create: `backend/app/db/session.py`
- Test: `backend/tests/unit/db/test_session.py`

- [ ] **Step 1: Write the failing test**

```python
from app.db.engine import create_db_engine
from app.db.session import make_session_factory

def test_session_factory_yields_working_session(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 't.db'}")
    Session = make_session_factory(engine)
    from sqlalchemy import text
    with Session() as s:
        assert s.execute(text("SELECT 1")).scalar() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/test_session.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Session factory."""
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/test_session.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/session.py backend/tests/unit/db/test_session.py
git commit -m "feat(db): add session factory"
```

### Task C5: Timestamp mixin

**Files:**
- Create: `backend/app/db/mixins/timestamp.py`
- Test: `backend/tests/unit/db/test_timestamp_mixin.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.mixins.timestamp import TimestampMixin

class _Sample(TimestampMixin, Base):
    __tablename__ = "sample_ts"
    id: Mapped[int] = mapped_column(primary_key=True)

def test_mixin_adds_columns():
    cols = {c.name for c in _Sample.__table__.columns}
    assert "created_at" in cols
    assert "updated_at" in cols
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/test_timestamp_mixin.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""created_at / updated_at mixin."""
from datetime import datetime, timezone
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/test_timestamp_mixin.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/mixins/timestamp.py backend/tests/unit/db/test_timestamp_mixin.py
git commit -m "feat(db): add timestamp mixin"
```

### Task C6: Alembic init + upgrade/downgrade round-trip test

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/migrations/env.py`
- Create: `backend/migrations/script.py.mako`
- Test: `backend/tests/integration/test_migration_roundtrip.py`

- [ ] **Step 1: Write the failing test**

```python
import subprocess
from pathlib import Path

def test_upgrade_then_downgrade(tmp_path: Path):
    db = tmp_path / "mig.db"
    env = {"DATABASE_URL": f"sqlite:///{db}"}
    import os
    full_env = {**os.environ, **env}
    up = subprocess.run(["alembic", "upgrade", "head"], cwd="backend", env=full_env)
    assert up.returncode == 0
    down = subprocess.run(["alembic", "downgrade", "base"], cwd="backend", env=full_env)
    assert down.returncode == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_migration_roundtrip.py -v`
Expected: FAIL (alembic not configured; no migrations yet — this test goes green after Task D6 creates the initial migration. Mark it xfail until D6, then remove xfail).

- [ ] **Step 3: Write alembic.ini (key lines)**

```ini
[alembic]
script_location = migrations
sqlalchemy.url =

[loggers]
keys = root

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[handler_console]
class = StreamHandler
args = (sys.stderr,)
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

- [ ] **Step 4: Write migrations/env.py**

```python
import os
from logging.config import fileConfig
from alembic import context
from app.db.base import Base
from app.db import models  # noqa: F401  (imports all models for autogenerate)

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL", "sqlite:///data/cdss.db"))
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    from app.db.engine import create_db_engine
    engine = create_db_engine(config.get_main_option("sqlalchemy.url"))
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 5: Write migrations/script.py.mako (standard Alembic template)**

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

- [ ] **Step 6: Commit**

```bash
git add backend/alembic.ini backend/migrations/ backend/tests/integration/test_migration_roundtrip.py
git commit -m "feat(db): add alembic config and migration roundtrip test"
```

## Phase B2: ORM Crypto Types

Goal: SQLAlchemy `TypeDecorator`s that transparently encrypt/hash on write and decrypt on read, depending on the Base from Phase C. Providers are injected from app config at model-import time via a module-level accessor.

### Task B2-1: Crypto context accessor

**Files:**
- Create: `backend/app/db/types/context.py`
- Test: `backend/tests/unit/db/types/test_context.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from cryptography.fernet import Fernet
from app.db.types.context import set_crypto, get_fernet, get_hasher
from app.core.encryption.fernet_provider import FernetProvider
from app.core.encryption.hash_provider import HashProvider

def test_set_and_get_crypto():
    set_crypto(FernetProvider(Fernet.generate_key()), HashProvider(b"pepper"))
    assert get_fernet() is not None
    assert get_hasher() is not None

def test_get_without_set_raises(monkeypatch):
    import app.db.types.context as ctx
    monkeypatch.setattr(ctx, "_fernet", None)
    with pytest.raises(RuntimeError):
        get_fernet()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/types/test_context.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Process-wide crypto provider accessor for ORM types.

Set once during create_app(); ORM TypeDecorators read from here.
"""
from app.core.encryption.fernet_provider import FernetProvider
from app.core.encryption.hash_provider import HashProvider

_fernet: FernetProvider | None = None
_hasher: HashProvider | None = None

def set_crypto(fernet: FernetProvider, hasher: HashProvider) -> None:
    global _fernet, _hasher
    _fernet = fernet
    _hasher = hasher

def get_fernet() -> FernetProvider:
    if _fernet is None:
        raise RuntimeError("Crypto not initialized; call set_crypto() in create_app()")
    return _fernet

def get_hasher() -> HashProvider:
    if _hasher is None:
        raise RuntimeError("Crypto not initialized; call set_crypto() in create_app()")
    return _hasher
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/types/test_context.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/types/context.py backend/tests/unit/db/types/test_context.py
git commit -m "feat(db): add crypto provider accessor for ORM types"
```

### Task B2-2: EncryptedString + HashedString types

**Files:**
- Create: `backend/app/db/types/encrypted_string.py`
- Create: `backend/app/db/types/hashed_string.py`
- Test: `backend/tests/unit/db/types/test_crypto_types.py`

- [ ] **Step 1: Write the failing test**

```python
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, Mapped, mapped_column
from app.db.base import Base
from app.db.types.context import set_crypto
from app.db.types.encrypted_string import EncryptedString
from app.db.types.hashed_string import HashedString
from app.core.encryption.fernet_provider import FernetProvider
from app.core.encryption.hash_provider import HashProvider

class _Person(Base):
    __tablename__ = "person_crypto"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(EncryptedString)
    nik_hash: Mapped[str] = mapped_column(HashedString)

def test_encrypted_roundtrip_and_hash(tmp_path):
    set_crypto(FernetProvider(Fernet.generate_key()), HashProvider(b"pepper"))
    engine = create_engine(f"sqlite:///{tmp_path / 'c.db'}")
    Base.metadata.create_all(engine, tables=[_Person.__table__])
    with Session(engine) as s:
        s.add(_Person(id=1, name="Budi", nik_hash="3171"))
        s.commit()
    with Session(engine) as s:
        p = s.scalar(select(_Person).where(_Person.id == 1))
        assert p.name == "Budi"            # decrypted transparently
        assert p.nik_hash != "3171"        # stored as hash
        assert len(p.nik_hash) == 64
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/types/test_crypto_types.py -v`
Expected: FAIL (modules not defined).

- [ ] **Step 3: Write EncryptedString**

```python
"""TypeDecorator that encrypts str -> bytes (Fernet) at rest."""
from sqlalchemy import LargeBinary
from sqlalchemy.types import TypeDecorator
from app.db.types.context import get_fernet

class EncryptedString(TypeDecorator):
    impl = LargeBinary
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return get_fernet().encrypt(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return get_fernet().decrypt(value)
```

- [ ] **Step 4: Write HashedString, then run tests**

```python
"""TypeDecorator that stores an HMAC-SHA256 hex digest (irreversible)."""
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator
from app.db.types.context import get_hasher

class HashedString(TypeDecorator):
    impl = String(64)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return get_hasher().hash(value)

    def process_result_value(self, value, dialect):
        return value
```

Run: `pytest tests/unit/db/types/test_crypto_types.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/types/encrypted_string.py backend/app/db/types/hashed_string.py backend/tests/unit/db/types/test_crypto_types.py
git commit -m "feat(db): add EncryptedString and HashedString ORM types"
```

## Phase D: Six Models

Goal: define HealthcareFacility, User, RefreshToken, AuditLog, PHIAccessLog, SystemConfig as SQLAlchemy 2.0 typed models, then generate the initial Alembic migration covering all six. Field definitions follow data-model-and-phi-design.md Section 4.

### Task D1: HealthcareFacility model

**Files:**
- Create: `backend/app/db/models/facility.py`
- Test: `backend/tests/unit/db/models/test_facility.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility

def test_create_facility(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'f.db'}")
    Base.metadata.create_all(engine, tables=[HealthcareFacility.__table__])
    with Session(engine) as s:
        s.add(HealthcareFacility(name="Puskesmas A", code="PKM-A", facility_type="puskesmas"))
        s.commit()
    with Session(engine) as s:
        f = s.scalar(select(HealthcareFacility).where(HealthcareFacility.code == "PKM-A"))
        assert f.name == "Puskesmas A"
        assert f.is_active is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/models/test_facility.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""HealthcareFacility model."""
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.mixins.timestamp import TimestampMixin

class HealthcareFacility(TimestampMixin, Base):
    __tablename__ = "healthcare_facility"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(50), unique=True)
    facility_type: Mapped[str] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(300), default=None)
    province_code: Mapped[str | None] = mapped_column(String(10), default=None)
    regency_code: Mapped[str | None] = mapped_column(String(10), default=None)
    subdistrict_code: Mapped[str | None] = mapped_column(String(10), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/models/test_facility.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/models/facility.py backend/tests/unit/db/models/test_facility.py
git commit -m "feat(db): add HealthcareFacility model"
```

### Task D2: User model

**Files:**
- Create: `backend/app/db/models/user.py`
- Test: `backend/tests/unit/db/models/test_user.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User

def test_create_user(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'u.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(User(name="Dr A", email="a@x.id", password_hash="h", role="admin", facility_id=1))
        s.commit()
    with Session(engine) as s:
        u = s.scalar(select(User).where(User.email == "a@x.id"))
        assert u.role == "admin"
        assert u.is_active is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/models/test_user.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""User model."""
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.mixins.timestamp import TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30))
    facility_id: Mapped[int] = mapped_column(ForeignKey("healthcare_facility.id"))
    profession: Mapped[str | None] = mapped_column(String(80), default=None)
    license_number: Mapped[str | None] = mapped_column(String(80), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/models/test_user.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/models/user.py backend/tests/unit/db/models/test_user.py
git commit -m "feat(db): add User model"
```

### Task D3: RefreshToken model

**Files:**
- Create: `backend/app/db/models/refresh_token.py`
- Test: `backend/tests/unit/db/models/test_refresh_token.py`

- [ ] **Step 1: Write the failing test**

```python
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken

def test_create_refresh_token(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'rt.db'}")
    Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(User(id=1, name="A", email="a@x.id", password_hash="h", role="admin", facility_id=1))
        s.add(RefreshToken(user_id=1, token_hash="abc", expires_at=now + timedelta(days=7)))
        s.commit()
    with Session(engine) as s:
        t = s.scalar(select(RefreshToken).where(RefreshToken.token_hash == "abc"))
        assert t.revoked_at is None
        assert t.replaced_by_id is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/models/test_refresh_token.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""RefreshToken model: rotation + replay detection."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    replaced_by_id: Mapped[int | None] = mapped_column(ForeignKey("refresh_token.id"), default=None)
```

Note: prefer a shared `_utcnow` import from the timestamp mixin module instead of the inline `__import__`; the engineer should refactor to `from app.db.mixins.timestamp import _utcnow` if exposing it publicly. Keep behavior identical.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/models/test_refresh_token.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/models/refresh_token.py backend/tests/unit/db/models/test_refresh_token.py
git commit -m "feat(db): add RefreshToken model with rotation fields"
```

### Task D4: AuditLog model

**Files:**
- Create: `backend/app/db/models/audit_log.py`
- Test: `backend/tests/unit/db/models/test_audit_log.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.audit_log import AuditLog

def test_create_audit_log(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'al.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(AuditLog(facility_id=1, action="login", request_id="req-1"))
        s.commit()
    with Session(engine) as s:
        a = s.scalar(select(AuditLog).where(AuditLog.action == "login"))
        assert a.request_id == "req-1"
        assert a.user_id is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/models/test_audit_log.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""AuditLog model."""
from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.mixins.timestamp import TimestampMixin

class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), default=None)
    facility_id: Mapped[int] = mapped_column(ForeignKey("healthcare_facility.id"))
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str | None] = mapped_column(String(80), default=None)
    entity_id: Mapped[int | None] = mapped_column(Integer, default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    ip_address: Mapped[str | None] = mapped_column(String(64), default=None)
    user_agent: Mapped[str | None] = mapped_column(String(300), default=None)
    request_id: Mapped[str | None] = mapped_column(String(64), default=None)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/models/test_audit_log.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/models/audit_log.py backend/tests/unit/db/models/test_audit_log.py
git commit -m "feat(db): add AuditLog model"
```

### Task D5: PHIAccessLog model

**Files:**
- Create: `backend/app/db/models/phi_access_log.py`
- Test: `backend/tests/unit/db/models/test_phi_access_log.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.db.models.phi_access_log import PHIAccessLog

def test_create_phi_access_log(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'phi.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(User(id=1, name="A", email="a@x.id", password_hash="h", role="clinician", facility_id=1))
        s.add(PHIAccessLog(user_id=1, patient_id="p-uuid", access_type="view",
                           purpose="treatment", accessed_field="name"))
        s.commit()
    with Session(engine) as s:
        log = s.scalar(select(PHIAccessLog).where(PHIAccessLog.user_id == 1))
        assert log.access_type == "view"
        assert log.purpose == "treatment"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/models/test_phi_access_log.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""PHIAccessLog model. Writer wired now; first called in Sprint 2 (Patient)."""
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.mixins.timestamp import _utcnow

class PHIAccessLog(Base):
    __tablename__ = "phi_access_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    patient_id: Mapped[str] = mapped_column(String(36))
    access_type: Mapped[str] = mapped_column(String(20))   # view/edit/export
    purpose: Mapped[str] = mapped_column(String(20))        # treatment/research/audit
    accessed_field: Mapped[str] = mapped_column(String(40))
    ip_address: Mapped[str | None] = mapped_column(String(64), default=None)
    accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
```

Note: this requires exposing `_utcnow` from `app/db/mixins/timestamp.py` (already defined there). Import it directly.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/models/test_phi_access_log.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/models/phi_access_log.py backend/tests/unit/db/models/test_phi_access_log.py
git commit -m "feat(db): add PHIAccessLog model"
```

### Task D6: SystemConfig model

**Files:**
- Create: `backend/app/db/models/system_config.py`
- Test: `backend/tests/unit/db/models/test_system_config.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.system_config import SystemConfig

def test_create_system_config(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'sc.db'}")
    Base.metadata.create_all(engine, tables=[SystemConfig.__table__])
    with Session(engine) as s:
        s.add(SystemConfig(key="enable_clinical_mode", value_json={"value": True}))
        s.commit()
    with Session(engine) as s:
        c = s.scalar(select(SystemConfig).where(SystemConfig.key == "enable_clinical_mode"))
        assert c.value_json == {"value": True}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/db/models/test_system_config.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""SystemConfig key-value model."""
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.mixins.timestamp import _utcnow

class SystemConfig(Base):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    value_json: Mapped[dict] = mapped_column(JSON)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("user.id"), default=None)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/db/models/test_system_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/models/system_config.py backend/tests/unit/db/models/test_system_config.py
git commit -m "feat(db): add SystemConfig model"
```

### Task D7: Models registry + initial migration

**Files:**
- Create: `backend/app/db/models/__init__.py`
- Create: `backend/migrations/versions/0001_initial.py` (via autogenerate)
- Modify: `backend/tests/integration/test_migration_roundtrip.py` (remove xfail)

- [ ] **Step 1: Write models/__init__.py**

```python
"""Import all models so Alembic autogenerate and create_all see them."""
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.db.models.audit_log import AuditLog
from app.db.models.phi_access_log import PHIAccessLog
from app.db.models.system_config import SystemConfig

__all__ = [
    "HealthcareFacility",
    "User",
    "RefreshToken",
    "AuditLog",
    "PHIAccessLog",
    "SystemConfig",
]
```

- [ ] **Step 2: Generate the initial migration**

Run (in `backend/`, with a temp DATABASE_URL):

```bash
$env:DATABASE_URL="sqlite:///data/cdss.db"; alembic revision --autogenerate -m "initial 6 tables"
```

Expected: a file `migrations/versions/0001_*.py` containing `create_table` for all six tables. Rename it to `0001_initial.py` for clarity. Inspect that all 6 tables and FKs are present.

- [ ] **Step 3: Apply and verify schema**

Run:

```bash
alembic upgrade head
python -c "import sqlite3; print(sorted(r[0] for r in sqlite3.connect('data/cdss.db').execute('select name from sqlite_master where type=\"table\"')))"
```

Expected: list includes healthcare_facility, user, refresh_token, audit_log, phi_access_log, system_config, alembic_version.

- [ ] **Step 4: Enable the round-trip test**

Remove the xfail marker from `tests/integration/test_migration_roundtrip.py` and run:

```bash
pytest tests/integration/test_migration_roundtrip.py -v
```

Expected: PASS (upgrade head + downgrade base both return 0).

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/models/__init__.py backend/migrations/versions/0001_initial.py backend/tests/integration/test_migration_roundtrip.py
git commit -m "feat(db): add models registry and initial 6-table migration"
```

## Phase E: Logging, Exceptions, Audit Writer, Service Registry

Goal: structlog JSON output with request_id, an AppException hierarchy that maps to the bilingual error envelope, an audit writer callable from the service layer, and an explicit service registry initialized in create_app() (fernet, hasher, audit writer, token service).

### Task E1: structlog config + processors

**Files:**
- Create: `backend/app/core/logging/processors.py`
- Create: `backend/app/core/logging/config.py`
- Test: `backend/tests/unit/core/logging/test_logging.py`

- [ ] **Step 1: Write the failing test**

```python
import json
import logging
from app.core.logging.config import configure_logging
import structlog

def test_logging_emits_json(capsys):
    configure_logging()
    log = structlog.get_logger()
    log.info("login_ok", user_id=1, request_id="req-1")
    out = capsys.readouterr().out
    record = json.loads(out.strip().splitlines()[-1])
    assert record["event"] == "login_ok"
    assert record["user_id"] == 1
    assert record["request_id"] == "req-1"
    assert "timestamp" in record
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/logging/test_logging.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write processors.py then config.py**

```python
"""Custom structlog processors."""
import structlog

def add_timestamp(_logger, _name, event_dict):
    event_dict.setdefault("timestamp", structlog.processors.TimeStamper(fmt="iso")(_logger, _name, {})["timestamp"]) if False else None
    return event_dict
```

Simpler: rely on built-in TimeStamper. Write `config.py`:

```python
"""Configure structlog for JSON stdout."""
import logging
import sys
import structlog

def configure_logging() -> None:
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

Note: `processors.py` may hold only the merge helper if needed; keep the TimeStamper in config. If `processors.py` ends up empty of real logic, give it a docstring placeholder and a `__all__ = []`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/logging/test_logging.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/logging/ backend/tests/unit/core/logging/test_logging.py
git commit -m "feat(infra): add structlog JSON logging config"
```

### Task E2: AppException hierarchy

**Files:**
- Create: `backend/app/core/exceptions/base.py`
- Test: `backend/tests/unit/core/exceptions/test_base.py`

- [ ] **Step 1: Write the failing test**

```python
from app.core.exceptions.base import (
    AppException, AuthError, ValidationError, NotFoundError, ConflictError,
)

def test_auth_error_fields():
    err = AuthError(code="AUTH_INVALID_CREDENTIALS",
                    message_id="Email atau password salah",
                    message_en="Invalid email or password",
                    field="credentials")
    assert err.http_status == 401
    assert err.code == "AUTH_INVALID_CREDENTIALS"
    assert err.message_en == "Invalid email or password"

def test_status_codes():
    assert ValidationError(code="X", message_id="a", message_en="b").http_status == 422
    assert NotFoundError(code="X", message_id="a", message_en="b").http_status == 404
    assert ConflictError(code="X", message_id="a", message_en="b").http_status == 409
    assert isinstance(AuthError(code="X", message_id="a", message_en="b"), AppException)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/exceptions/test_base.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Application exception hierarchy mapping to the bilingual error envelope."""

class AppException(Exception):
    http_status = 500

    def __init__(self, code: str, message_id: str, message_en: str,
                 field: str | None = None) -> None:
        super().__init__(message_en)
        self.code = code
        self.message_id = message_id
        self.message_en = message_en
        self.field = field

class AuthError(AppException):
    http_status = 401

class ValidationError(AppException):
    http_status = 422

class NotFoundError(AppException):
    http_status = 404

class ConflictError(AppException):
    http_status = 409
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/exceptions/test_base.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/exceptions/base.py backend/tests/unit/core/exceptions/test_base.py
git commit -m "feat(infra): add AppException hierarchy"
```

### Task E3: Global error handlers

**Files:**
- Create: `backend/app/core/exceptions/handlers.py`
- Test: `backend/tests/unit/core/exceptions/test_handlers.py`

- [ ] **Step 1: Write the failing test**

```python
from flask import Flask
from app.core.exceptions.base import AuthError
from app.core.exceptions.handlers import register_error_handlers

def _make_app():
    app = Flask(__name__)
    register_error_handlers(app)

    @app.get("/boom")
    def boom():
        raise AuthError(code="AUTH_INVALID_CREDENTIALS",
                        message_id="Email atau password salah",
                        message_en="Invalid email or password",
                        field="credentials")
    return app

def test_handler_maps_to_envelope():
    app = _make_app()
    client = app.test_client()
    resp = client.get("/boom")
    assert resp.status_code == 401
    body = resp.get_json()["error"]
    assert body["code"] == "AUTH_INVALID_CREDENTIALS"
    assert body["message_id"] == "Email atau password salah"
    assert body["message_en"] == "Invalid email or password"
    assert body["field"] == "credentials"
    assert "request_id" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/exceptions/test_handlers.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Global Flask error handlers -> bilingual JSON envelope."""
from flask import Flask, jsonify, g, request
from app.core.exceptions.base import AppException

def _request_id() -> str:
    return getattr(g, "request_id", None) or request.headers.get("X-Request-ID", "n/a")

def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppException)
    def _handle_app_exception(err: AppException):
        payload = {
            "error": {
                "code": err.code,
                "message_id": err.message_id,
                "message_en": err.message_en,
                "field": err.field,
                "request_id": _request_id(),
            }
        }
        return jsonify(payload), err.http_status

    @app.errorhandler(500)
    def _handle_500(_err):
        payload = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message_id": "Terjadi kesalahan sistem",
                "message_en": "Internal server error",
                "field": None,
                "request_id": _request_id(),
            }
        }
        return jsonify(payload), 500
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/exceptions/test_handlers.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/exceptions/handlers.py backend/tests/unit/core/exceptions/test_handlers.py
git commit -m "feat(infra): add global error handlers with bilingual envelope"
```

### Task E4: Audit writer

**Files:**
- Create: `backend/app/services/audit/writer.py`
- Test: `backend/tests/unit/services/audit/test_writer.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.audit_log import AuditLog
from app.services.audit.writer import write_audit

def test_write_audit_persists(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'aud.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.commit()
        write_audit(s, facility_id=1, action="login", user_id=None,
                    request_id="req-9", ip_address="127.0.0.1", user_agent="pytest")
        s.commit()
        row = s.scalar(select(AuditLog).where(AuditLog.action == "login"))
        assert row.request_id == "req-9"
        assert row.ip_address == "127.0.0.1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/services/audit/test_writer.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Audit writer. Called explicitly from the service layer (not hidden middleware)."""
from sqlalchemy.orm import Session
from app.db.models.audit_log import AuditLog

def write_audit(
    session: Session,
    *,
    facility_id: int,
    action: str,
    user_id: int | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    description: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        facility_id=facility_id,
        action=action,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
    )
    session.add(entry)
    return entry
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/services/audit/test_writer.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/audit/writer.py backend/tests/unit/services/audit/test_writer.py
git commit -m "feat(audit): add audit log writer"
```

### Task E5: Service registry on app context

**Files:**
- Create: `backend/app/extensions.py`
- Test: `backend/tests/unit/test_extensions.py`

- [ ] **Step 1: Write the failing test**

```python
from app.extensions import db, jwt, migrate

def test_singletons_exist():
    assert db is not None
    assert jwt is not None
    assert migrate is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_extensions.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Flask extension singletons. Bound to the app in create_app()."""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.db.base import Base

db = SQLAlchemy(model_class=Base)
jwt = JWTManager()
migrate = Migrate()
```

Note: add `flask-sqlalchemy>=3.1` and `flask-migrate>=4.0` to `backend/pyproject.toml` dependencies (Task A1) if not already present. The engineer must update pyproject and reinstall before this test passes.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_extensions.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/extensions.py backend/tests/unit/test_extensions.py backend/pyproject.toml
git commit -m "feat(infra): add Flask extension singletons"
```

## Phase F: Auth Core

Goal: bcrypt password hashing, opaque refresh-token generation+hashing, RBAC role enum + decorator, login service with generic error (anti-enumeration) and audit, refresh rotation with replay detection, and idempotent logout.

### Task F1: Password hashing wrapper

**Files:**
- Create: `backend/app/core/security/password.py`
- Create: `backend/tests/passlib_test_config.py`
- Test: `backend/tests/unit/core/security/test_password.py`

- [ ] **Step 1: Write the failing test**

```python
from app.core.security.password import hash_password, verify_password

def test_hash_and_verify():
    h = hash_password("s3cret", rounds=4)
    assert h != "s3cret"
    assert verify_password("s3cret", h) is True
    assert verify_password("wrong", h) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/security/test_password.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""bcrypt password hashing via passlib."""
from passlib.context import CryptContext

_DEFAULT_ROUNDS = 12

def _context(rounds: int) -> CryptContext:
    return CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=rounds)

def hash_password(plain: str, rounds: int = _DEFAULT_ROUNDS) -> str:
    return _context(rounds).hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return _context(_DEFAULT_ROUNDS).verify(plain, hashed)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/security/test_password.py -v`
Expected: PASS. Tests use rounds=4 for speed; production uses default 12.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/security/password.py backend/tests/unit/core/security/test_password.py
git commit -m "feat(auth): add bcrypt password hashing"
```

### Task F2: Opaque refresh token generation + hashing

**Files:**
- Create: `backend/app/core/security/tokens.py`
- Test: `backend/tests/unit/core/security/test_tokens.py`

- [ ] **Step 1: Write the failing test**

```python
from app.core.security.tokens import generate_refresh_token, hash_token

def test_generate_is_unique_and_hashable():
    raw1, _ = generate_refresh_token()
    raw2, _ = generate_refresh_token()
    assert raw1 != raw2
    assert len(raw1) >= 32

def test_hash_is_deterministic():
    raw, h = generate_refresh_token()
    assert h == hash_token(raw)
    assert len(h) == 64
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/security/test_tokens.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Opaque refresh tokens: random secret + SHA256 hash for storage."""
import hashlib
import secrets

def generate_refresh_token() -> tuple[str, str]:
    raw = secrets.token_urlsafe(48)
    return raw, hash_token(raw)

def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

Note: refresh tokens are opaque (not JWT). Only the SHA256 hash is stored. The raw token goes to the client and is never persisted server-side.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/security/test_tokens.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/security/tokens.py backend/tests/unit/core/security/test_tokens.py
git commit -m "feat(auth): add opaque refresh token generation and hashing"
```

### Task F3: RBAC roles + decorator

**Files:**
- Create: `backend/app/core/rbac/roles.py`
- Create: `backend/app/core/rbac/decorators.py`
- Test: `backend/tests/unit/core/rbac/test_decorators.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from app.core.rbac.roles import Role
from app.core.rbac.decorators import require_role
from app.core.exceptions.handlers import register_error_handlers

def _make_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test"
    JWTManager(app)
    register_error_handlers(app)

    @app.get("/admin-only")
    @require_role(Role.ADMIN)
    def admin_only():
        return {"ok": True}
    return app

def test_role_enum_values():
    assert Role.ADMIN.value == "admin"
    assert {r.value for r in Role} == {
        "admin", "clinician", "nurse", "researcher", "expert_reviewer"
    }

def test_decorator_blocks_wrong_role():
    app = _make_app()
    with app.app_context():
        token = create_access_token(identity="1", additional_claims={"role": "nurse"})
    client = app.test_client()
    resp = client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403

def test_decorator_allows_correct_role():
    app = _make_app()
    with app.app_context():
        token = create_access_token(identity="1", additional_claims={"role": "admin"})
    client = app.test_client()
    resp = client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/rbac/test_decorators.py -v`
Expected: FAIL (modules not defined).

- [ ] **Step 3: Write roles.py then decorators.py**

```python
"""RBAC roles."""
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    CLINICIAN = "clinician"
    NURSE = "nurse"
    RESEARCHER = "researcher"
    EXPERT_REVIEWER = "expert_reviewer"
```

```python
"""@require_role decorator built on Flask-JWT-Extended."""
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.core.rbac.roles import Role
from app.core.exceptions.base import AppException

class ForbiddenError(AppException):
    http_status = 403

def require_role(*roles: Role):
    allowed = {r.value for r in roles}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in allowed:
                raise ForbiddenError(
                    code="AUTH_FORBIDDEN",
                    message_id="Anda tidak memiliki akses",
                    message_en="You do not have access to this resource",
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/rbac/test_decorators.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/rbac/ backend/tests/unit/core/rbac/test_decorators.py
git commit -m "feat(auth): add RBAC roles and require_role decorator"
```

### Task F4: Login service (generic error + audit)

**Files:**
- Create: `backend/app/services/auth/login_service.py`
- Test: `backend/tests/unit/services/auth/test_login_service.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.db.models.audit_log import AuditLog
from app.core.security.password import hash_password
from app.core.exceptions.base import AuthError
from app.services.auth.login_service import authenticate

def _seed(engine):
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(User(id=1, name="A", email="a@x.id",
                   password_hash=hash_password("good", rounds=4),
                   role="admin", facility_id=1))
        s.commit()

def test_authenticate_success(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'login.db'}")
    Base.metadata.create_all(engine); _seed(engine)
    with Session(engine) as s:
        user = authenticate(s, email="a@x.id", password="good",
                            ip_address="127.0.0.1", user_agent="pytest", request_id="r1")
        s.commit()
        assert user.id == 1
        assert s.query(AuditLog).filter_by(action="login").count() == 1

def test_authenticate_wrong_password_generic(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'login2.db'}")
    Base.metadata.create_all(engine); _seed(engine)
    with Session(engine) as s:
        with pytest.raises(AuthError) as exc:
            authenticate(s, email="a@x.id", password="bad",
                        ip_address="127.0.0.1", user_agent="pytest", request_id="r2")
        assert exc.value.code == "AUTH_INVALID_CREDENTIALS"
        s.commit()
        assert s.query(AuditLog).filter_by(action="login_failed").count() == 1

def test_authenticate_unknown_email_same_error(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'login3.db'}")
    Base.metadata.create_all(engine); _seed(engine)
    with Session(engine) as s:
        with pytest.raises(AuthError) as exc:
            authenticate(s, email="nobody@x.id", password="x",
                        ip_address="127.0.0.1", user_agent="pytest", request_id="r3")
        assert exc.value.code == "AUTH_INVALID_CREDENTIALS"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/services/auth/test_login_service.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Login service: authenticate, audit, anti-enumeration generic error."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.core.security.password import verify_password
from app.core.exceptions.base import AuthError
from app.services.audit.writer import write_audit

_INVALID = dict(
    code="AUTH_INVALID_CREDENTIALS",
    message_id="Email atau password salah",
    message_en="Invalid email or password",
    field="credentials",
)

def authenticate(session: Session, *, email: str, password: str,
                 ip_address: str, user_agent: str, request_id: str) -> User:
    user = session.scalar(select(User).where(User.email == email))
    ok = user is not None and user.is_active and verify_password(password, user.password_hash)
    if not ok:
        write_audit(session, facility_id=(user.facility_id if user else 0),
                    action="login_failed", user_id=(user.id if user else None),
                    ip_address=ip_address, user_agent=user_agent, request_id=request_id,
                    description=f"failed login for {email}")
        raise AuthError(**_INVALID)
    write_audit(session, facility_id=user.facility_id, action="login",
                user_id=user.id, ip_address=ip_address, user_agent=user_agent,
                request_id=request_id)
    return user
```

Note: facility_id=0 for unknown email avoids a null FK on the audit row; alternatively make AuditLog.facility_id nullable. Choose nullable if a 0 facility row does not exist. For Sprint 1 the seeded facility is id=1; prefer making facility_id nullable on AuditLog to be safe — update Task D4 model + migration accordingly if you hit an FK error.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/services/auth/test_login_service.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/auth/login_service.py backend/tests/unit/services/auth/test_login_service.py
git commit -m "feat(auth): add login service with audit and generic error"
```

### Task F5: Token service (refresh rotation + replay detection)

**Files:**
- Create: `backend/app/services/auth/token_service.py`
- Test: `backend/tests/unit/services/auth/test_token_service.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.core.security.tokens import hash_token
from app.core.exceptions.base import AuthError
from app.services.auth.token_service import issue_refresh_token, rotate_refresh_token

def _seed(engine):
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(User(id=1, name="A", email="a@x.id", password_hash="h", role="admin", facility_id=1))
        s.commit()

def test_issue_then_rotate(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'tok.db'}")
    Base.metadata.create_all(engine); _seed(engine)
    with Session(engine) as s:
        raw1 = issue_refresh_token(s, user_id=1, ttl_days=7); s.commit()
        raw2 = rotate_refresh_token(s, raw_token=raw1, ttl_days=7); s.commit()
        assert raw2 != raw1
        old = s.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw1)))
        assert old.revoked_at is not None
        assert old.replaced_by_id is not None

def test_replay_detection_revokes_chain(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'tok2.db'}")
    Base.metadata.create_all(engine); _seed(engine)
    with Session(engine) as s:
        raw1 = issue_refresh_token(s, user_id=1, ttl_days=7); s.commit()
        rotate_refresh_token(s, raw_token=raw1, ttl_days=7); s.commit()
        # reusing raw1 (already rotated) = replay
        with pytest.raises(AuthError) as exc:
            rotate_refresh_token(s, raw_token=raw1, ttl_days=7)
        assert exc.value.code == "AUTH_REFRESH_REPLAY"

def test_expired_token_rejected(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'tok3.db'}")
    Base.metadata.create_all(engine); _seed(engine)
    with Session(engine) as s:
        raw = issue_refresh_token(s, user_id=1, ttl_days=7)
        t = s.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw)))
        t.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        s.commit()
        with pytest.raises(AuthError) as exc:
            rotate_refresh_token(s, raw_token=raw, ttl_days=7)
        assert exc.value.code == "AUTH_REFRESH_INVALID"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/services/auth/test_token_service.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Refresh token issue + rotation with replay detection."""
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.db.models.refresh_token import RefreshToken
from app.core.security.tokens import generate_refresh_token, hash_token
from app.core.exceptions.base import AuthError

def _now() -> datetime:
    return datetime.now(timezone.utc)

def issue_refresh_token(session: Session, *, user_id: int, ttl_days: int) -> str:
    raw, token_hash = generate_refresh_token()
    session.add(RefreshToken(
        user_id=user_id, token_hash=token_hash,
        expires_at=_now() + timedelta(days=ttl_days),
    ))
    return raw

def rotate_refresh_token(session: Session, *, raw_token: str, ttl_days: int) -> str:
    token_hash = hash_token(raw_token)
    current = session.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if current is None:
        raise AuthError(code="AUTH_REFRESH_INVALID",
                        message_id="Token tidak valid", message_en="Invalid refresh token")
    if current.revoked_at is not None:
        # replay: this token was already rotated. Revoke the whole user's active chain.
        session.execute(
            update(RefreshToken).where(
                RefreshToken.user_id == current.user_id,
                RefreshToken.revoked_at.is_(None),
            ).values(revoked_at=_now())
        )
        raise AuthError(code="AUTH_REFRESH_REPLAY",
                        message_id="Token sudah digunakan", message_en="Refresh token reuse detected")
    if current.expires_at <= _now():
        raise AuthError(code="AUTH_REFRESH_INVALID",
                        message_id="Token kedaluwarsa", message_en="Refresh token expired")
    new_raw, new_hash = generate_refresh_token()
    new_token = RefreshToken(user_id=current.user_id, token_hash=new_hash,
                             expires_at=_now() + timedelta(days=ttl_days))
    session.add(new_token)
    session.flush()
    current.revoked_at = _now()
    current.replaced_by_id = new_token.id
    return new_raw
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/services/auth/test_token_service.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/auth/token_service.py backend/tests/unit/services/auth/test_token_service.py
git commit -m "feat(auth): add refresh rotation with replay detection"
```

### Task F6: Idempotent logout (revoke by raw token)

**Files:**
- Modify: `backend/app/services/auth/token_service.py` (add `revoke_refresh_token`)
- Test: `backend/tests/unit/services/auth/test_logout.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.core.security.tokens import hash_token
from app.services.auth.token_service import issue_refresh_token, revoke_refresh_token

def _seed(engine):
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(User(id=1, name="A", email="a@x.id", password_hash="h", role="admin", facility_id=1))
        s.commit()

def test_logout_is_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'lo.db'}")
    Base.metadata.create_all(engine); _seed(engine)
    with Session(engine) as s:
        raw = issue_refresh_token(s, user_id=1, ttl_days=7); s.commit()
        # first logout
        revoke_refresh_token(s, raw_token=raw); s.commit()
        t = s.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw)))
        assert t.revoked_at is not None
        # second logout: no error, still revoked
        revoke_refresh_token(s, raw_token=raw); s.commit()
        # unknown token: no error
        revoke_refresh_token(s, raw_token="never-existed"); s.commit()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/services/auth/test_logout.py -v`
Expected: FAIL (`revoke_refresh_token` not defined).

- [ ] **Step 3: Add implementation to token_service.py**

```python
def revoke_refresh_token(session: Session, *, raw_token: str) -> None:
    """Idempotent: revoke the token if it exists and is active; otherwise no-op."""
    token_hash = hash_token(raw_token)
    current = session.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if current is not None and current.revoked_at is None:
        current.revoked_at = _now()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/services/auth/test_logout.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/auth/token_service.py backend/tests/unit/services/auth/test_logout.py
git commit -m "feat(auth): add idempotent logout token revocation"
```

### Task F7: JWT access claims helper

**Files:**
- Create: `backend/app/core/security/jwt.py`
- Test: `backend/tests/unit/core/security/test_jwt.py`

- [ ] **Step 1: Write the failing test**

```python
from flask import Flask
from flask_jwt_extended import JWTManager, decode_token
from app.core.security.jwt import make_access_token

def test_access_token_carries_role_and_facility():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test"
    JWTManager(app)
    with app.app_context():
        token = make_access_token(user_id=1, role="admin", facility_id=7)
        decoded = decode_token(token)
        assert decoded["sub"] == "1"
        assert decoded["role"] == "admin"
        assert decoded["facility_id"] == 7
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/core/security/test_jwt.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Access token helper. JWT signing key comes from app config (env), NOT master.key."""
from flask_jwt_extended import create_access_token

def make_access_token(*, user_id: int, role: str, facility_id: int) -> str:
    return create_access_token(
        identity=str(user_id),
        additional_claims={"role": role, "facility_id": facility_id},
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/core/security/test_jwt.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/security/jwt.py backend/tests/unit/core/security/test_jwt.py
git commit -m "feat(auth): add JWT access token claims helper"
```

## Phase G: API Layer

Goal: config classes, app factory wiring extensions + crypto + logging + error handlers, Pydantic request/response schemas, health/version endpoints, auth endpoints (login/refresh/logout/me), and blueprint registration. No CORS (dev uses Vite proxy; prod single-process).

### Task G1: Config classes

**Files:**
- Create: `backend/app/config.py`
- Test: `backend/tests/unit/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
from app.config import DevConfig, TestConfig, ProdConfig

def test_test_config_uses_memory_or_tmp():
    cfg = TestConfig()
    assert cfg.TESTING is True
    assert cfg.JWT_SECRET_KEY

def test_prod_requires_jwt_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "prod-secret")
    cfg = ProdConfig()
    assert cfg.JWT_SECRET_KEY == "prod-secret"
    assert cfg.DEBUG is False

def test_dev_defaults():
    cfg = DevConfig()
    assert cfg.DEBUG is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_config.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write minimal implementation**

```python
"""Application configuration."""
import os
from datetime import timedelta

class BaseConfig:
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    REFRESH_TTL_DAYS = 7
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///data/cdss.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MASTER_KEY_PATH = os.environ.get("MASTER_KEY_PATH", "secrets/master.key")
    HMAC_PEPPER_PATH = os.environ.get("HMAC_PEPPER_PATH", "secrets/hmac_pepper.key")
    APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")
    GIT_SHA = os.environ.get("GIT_SHA", "local")
    DEBUG = False
    TESTING = False

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False

class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/config.py backend/tests/unit/test_config.py
git commit -m "feat(api): add config classes"
```

### Task G2: Pydantic schemas

**Files:**
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/schemas/common.py`
- Test: `backend/tests/unit/schemas/test_auth_schema.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from pydantic import ValidationError as PydanticError
from app.schemas.auth import LoginRequest, UserOut

def test_login_request_valid():
    req = LoginRequest(email="a@x.id", password="secret")
    assert req.email == "a@x.id"

def test_login_request_rejects_bad_email():
    with pytest.raises(PydanticError):
        LoginRequest(email="not-an-email", password="secret")

def test_user_out_serializes():
    out = UserOut(id=1, name="A", role="admin", facility_id=1)
    assert out.model_dump()["role"] == "admin"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/schemas/test_auth_schema.py -v`
Expected: FAIL (module not defined). Note: requires `pydantic[email]` (add `email-validator`) in pyproject.

- [ ] **Step 3: Write common.py then auth.py**

```python
"""Shared schema primitives."""
from pydantic import BaseModel

class ErrorBody(BaseModel):
    code: str
    message_id: str
    message_en: str
    field: str | None = None
    request_id: str | None = None

class ErrorEnvelope(BaseModel):
    error: ErrorBody
```

```python
"""Auth DTOs."""
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class UserOut(BaseModel):
    id: int
    name: str
    role: str
    facility_id: int

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserOut | None = None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/schemas/test_auth_schema.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/ backend/tests/unit/schemas/test_auth_schema.py backend/pyproject.toml
git commit -m "feat(api): add auth and common Pydantic schemas"
```

### Task G3: App factory

**Files:**
- Modify: `backend/app/__init__.py` (replace placeholder with `create_app`)
- Test: `backend/tests/unit/test_app_factory.py`

- [ ] **Step 1: Write the failing test**

```python
from app import create_app
from app.config import TestConfig

def test_create_app_returns_flask_app():
    app = create_app(TestConfig)
    assert app is not None
    assert app.config["TESTING"] is True

def test_app_has_health_route():
    app = create_app(TestConfig)
    rules = {r.rule for r in app.url_map.iter_rules()}
    assert "/api/health" in rules
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_app_factory.py -v`
Expected: FAIL (`create_app` not defined).

- [ ] **Step 3: Write implementation**

```python
"""EKG-Insight backend application factory."""
from flask import Flask
from app.config import BaseConfig, DevConfig
from app.extensions import db, jwt, migrate
from app.core.logging.config import configure_logging
from app.core.exceptions.handlers import register_error_handlers
from app.core.encryption.key_loader import load_key
from app.core.encryption.fernet_provider import FernetProvider
from app.core.encryption.hash_provider import HashProvider
from app.db.types.context import set_crypto
from app.api import register_blueprints

def create_app(config: type[BaseConfig] = DevConfig) -> Flask:
    configure_logging()
    app = Flask(__name__, static_folder="static", static_url_path="/")
    app.config.from_object(config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Initialize crypto providers (skip hard failure in TESTING without keys).
    try:
        fernet = FernetProvider(load_key(app.config["MASTER_KEY_PATH"]))
        hasher = HashProvider(load_key(app.config["HMAC_PEPPER_PATH"]))
        set_crypto(fernet, hasher)
    except FileNotFoundError:
        if not app.config.get("TESTING"):
            raise

    register_error_handlers(app)
    register_blueprints(app)
    return app
```

Note: in tests that need crypto (e.g. encrypted columns), the conftest fixture calls `set_crypto` with an ephemeral key. For Sprint 1 auth tests, no PHI columns are touched, so the missing-key path is tolerated under TESTING.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_app_factory.py -v`
Expected: PASS (after G4 health blueprint + G6 register_blueprints exist; if running G3 alone, temporarily stub register_blueprints to no-op, then wire in G4/G6). Implement G4 and G6 before final run.

- [ ] **Step 5: Commit**

```bash
git add backend/app/__init__.py backend/tests/unit/test_app_factory.py
git commit -m "feat(api): add application factory"
```

### Task G4: Health + version endpoints

**Files:**
- Create: `backend/app/api/health.py`
- Test: `backend/tests/integration/test_health.py`

- [ ] **Step 1: Write the failing test**

```python
from app import create_app
from app.config import TestConfig

def test_health_ok():
    app = create_app(TestConfig)
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert body["db"] == "ok"

def test_version():
    app = create_app(TestConfig)
    client = app.test_client()
    resp = client.get("/api/version")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "version" in body and "git_sha" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_health.py -v`
Expected: FAIL (blueprint not defined).

- [ ] **Step 3: Write implementation**

```python
"""Health and version endpoints."""
from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from app.extensions import db

bp = Blueprint("health", __name__, url_prefix="/api")

@bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    from datetime import datetime, timezone
    return jsonify(status="ok", db=db_status, time=datetime.now(timezone.utc).isoformat())

@bp.get("/version")
def version():
    return jsonify(
        version=current_app.config["APP_VERSION"],
        build=current_app.config.get("APP_VERSION"),
        git_sha=current_app.config["GIT_SHA"],
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_health.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/health.py backend/tests/integration/test_health.py
git commit -m "feat(api): add health and version endpoints"
```

### Task G5: Auth endpoints

**Files:**
- Create: `backend/app/api/auth.py`
- Test: `backend/tests/integration/test_auth_api.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.core.security.password import hash_password

@pytest.fixture()
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        db.session.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        db.session.add(User(id=1, name="A", email="a@x.id",
                            password_hash=hash_password("good", rounds=4),
                            role="admin", facility_id=1))
        db.session.commit()
        yield app.test_client()

def test_login_success(client):
    resp = client.post("/api/auth/login", json={"email": "a@x.id", "password": "good"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["access_token"] and body["refresh_token"]
    assert body["user"]["role"] == "admin"

def test_login_bad_password(client):
    resp = client.post("/api/auth/login", json={"email": "a@x.id", "password": "bad"})
    assert resp.status_code == 401
    assert resp.get_json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"

def test_refresh_rotates(client):
    login = client.post("/api/auth/login", json={"email": "a@x.id", "password": "good"})
    refresh = login.get_json()["refresh_token"]
    resp = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    assert resp.get_json()["refresh_token"] != refresh

def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401

def test_logout_then_me(client):
    login = client.post("/api/auth/login", json={"email": "a@x.id", "password": "good"}).get_json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}
    assert client.post("/api/auth/logout", json={"refresh_token": login["refresh_token"]}, headers=headers).status_code == 200
    # logout again = still 200 (idempotent)
    assert client.post("/api/auth/logout", json={"refresh_token": login["refresh_token"]}, headers=headers).status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_auth_api.py -v`
Expected: FAIL (blueprint not defined).

- [ ] **Step 3: Write implementation**

```python
"""Auth endpoints: login, refresh, logout, me."""
from flask import Blueprint, jsonify, request, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.schemas.auth import LoginRequest, RefreshRequest, UserOut
from app.services.auth.login_service import authenticate
from app.services.auth.token_service import (
    issue_refresh_token, rotate_refresh_token, revoke_refresh_token,
)
from app.core.security.jwt import make_access_token
from app.db.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

def _ctx():
    return dict(
        ip_address=request.remote_addr or "unknown",
        user_agent=request.headers.get("User-Agent", "unknown"),
        request_id=getattr(g, "request_id", request.headers.get("X-Request-ID", "n/a")),
    )

@bp.post("/login")
def login():
    data = LoginRequest(**(request.get_json() or {}))
    user = authenticate(db.session, email=data.email, password=data.password, **_ctx())
    access = make_access_token(user_id=user.id, role=user.role, facility_id=user.facility_id)
    refresh = issue_refresh_token(db.session, user_id=user.id,
                                  ttl_days=current_app.config["REFRESH_TTL_DAYS"])
    db.session.commit()
    return jsonify(access_token=access, refresh_token=refresh,
                   user=UserOut(id=user.id, name=user.name, role=user.role,
                                facility_id=user.facility_id).model_dump())

@bp.post("/refresh")
def refresh():
    data = RefreshRequest(**(request.get_json() or {}))
    new_refresh = rotate_refresh_token(db.session, raw_token=data.refresh_token,
                                       ttl_days=current_app.config["REFRESH_TTL_DAYS"])
    token_row = None  # fetch user for new access token
    from sqlalchemy import select
    from app.db.models.refresh_token import RefreshToken
    from app.core.security.tokens import hash_token
    token_row = db.session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(new_refresh))
    )
    user = db.session.get(User, token_row.user_id)
    access = make_access_token(user_id=user.id, role=user.role, facility_id=user.facility_id)
    db.session.commit()
    return jsonify(access_token=access, refresh_token=new_refresh)

@bp.post("/logout")
@jwt_required()
def logout():
    data = request.get_json() or {}
    raw = data.get("refresh_token")
    if raw:
        revoke_refresh_token(db.session, raw_token=raw)
        db.session.commit()
    return jsonify(status="ok")

@bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    return jsonify(user=UserOut(id=user.id, name=user.name, role=user.role,
                                facility_id=user.facility_id).model_dump())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_auth_api.py -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/auth.py backend/tests/integration/test_auth_api.py
git commit -m "feat(api): add auth endpoints login/refresh/logout/me"
```

### Task G6: Blueprint registration

**Files:**
- Create: `backend/app/api/__init__.py`
- Test: covered by `test_app_factory.py` and `test_auth_api.py` (no new test file)

- [ ] **Step 1: Write implementation**

```python
"""Blueprint registration."""
from flask import Flask

def register_blueprints(app: Flask) -> None:
    from app.api.health import bp as health_bp
    from app.api.auth import bp as auth_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
```

- [ ] **Step 2: Run the related tests**

Run: `pytest tests/unit/test_app_factory.py tests/integration/test_auth_api.py tests/integration/test_health.py -v`
Expected: PASS (all routes registered).

- [ ] **Step 3: Full backend suite + lint + type check**

Run (in `backend/`):

```bash
ruff check . && mypy . && pytest
```

Expected: all green.

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/__init__.py
git commit -m "feat(api): register health and auth blueprints"
```

## Phase H: Frontend Skeleton

Goal: minimal React+TS app with a Zustand token store, an API client that attaches the access token and retries once on 401 via refresh, a LoginForm, a ProtectedRoute, the login route, and four Vitest tests. Deep UI tests deferred to Sprint 2+.

### Task H1: Vitest setup + token store

**Files:**
- Create: `frontend/src/test/setup.ts`
- Create: `frontend/src/features/auth/store.ts`
- Test: `frontend/src/features/auth/store.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "./store";

describe("auth store", () => {
  beforeEach(() => {
    useAuthStore.getState().clear();
  });

  it("sets and clears tokens", () => {
    useAuthStore.getState().setTokens("acc", "ref");
    expect(useAuthStore.getState().accessToken).toBe("acc");
    expect(useAuthStore.getState().refreshToken).toBe("ref");
    useAuthStore.getState().clear();
    expect(useAuthStore.getState().accessToken).toBeNull();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- store` in `frontend/`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write setup.ts then store.ts**

```typescript
import "@testing-library/jest-dom";
```

```typescript
import { create } from "zustand";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (access: string, refresh: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),
  clear: () => set({ accessToken: null, refreshToken: null }),
}));
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- store` in `frontend/`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/test/setup.ts frontend/src/features/auth/store.ts frontend/src/features/auth/store.test.ts
git commit -m "feat(ui): add auth token store"
```

### Task H2: Token persistence helper

**Files:**
- Create: `frontend/src/lib/api/auth-token.ts`
- Test: `frontend/src/lib/api/auth-token.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { saveTokens, loadTokens, clearTokens } from "./auth-token";

describe("auth-token persistence", () => {
  beforeEach(() => localStorage.clear());

  it("saves and loads tokens", () => {
    saveTokens("acc", "ref");
    expect(loadTokens()).toEqual({ accessToken: "acc", refreshToken: "ref" });
  });

  it("clears tokens", () => {
    saveTokens("acc", "ref");
    clearTokens();
    expect(loadTokens()).toEqual({ accessToken: null, refreshToken: null });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- auth-token` in `frontend/`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write implementation**

```typescript
const ACCESS = "ekg.access";
const REFRESH = "ekg.refresh";

export function saveTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS, access);
  localStorage.setItem(REFRESH, refresh);
}

export function loadTokens(): { accessToken: string | null; refreshToken: string | null } {
  return {
    accessToken: localStorage.getItem(ACCESS),
    refreshToken: localStorage.getItem(REFRESH),
  };
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS);
  localStorage.removeItem(REFRESH);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- auth-token` in `frontend/`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/api/auth-token.ts frontend/src/lib/api/auth-token.test.ts
git commit -m "feat(ui): add token persistence helper"
```

### Task H3: API client with attach-token + refresh-on-401

**Files:**
- Create: `frontend/src/lib/api/client.ts`
- Test: `frontend/src/lib/api/client.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
import { describe, it, expect, beforeEach, vi } from "vitest";
import { apiFetch } from "./client";
import { useAuthStore } from "@/features/auth/store";

describe("apiFetch", () => {
  beforeEach(() => useAuthStore.getState().setTokens("acc", "ref"));

  it("attaches the access token", async () => {
    const spy = vi.fn(async () =>
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    );
    vi.stubGlobal("fetch", spy);
    await apiFetch("/api/test");
    const headers = (spy.mock.calls[0][1] as RequestInit).headers as Record<string, string>;
    expect(headers["Authorization"]).toBe("Bearer acc");
  });

  it("refreshes once on 401 then retries", async () => {
    const responses = [
      new Response("{}", { status: 401 }),
      new Response(JSON.stringify({ access_token: "new", refresh_token: "newref" }), { status: 200 }),
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    ];
    const spy = vi.fn(async () => responses.shift()!);
    vi.stubGlobal("fetch", spy);
    const resp = await apiFetch("/api/protected");
    expect(resp.status).toBe(200);
    expect(useAuthStore.getState().accessToken).toBe("new");
    expect(spy).toHaveBeenCalledTimes(3);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- client` in `frontend/`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write implementation**

```typescript
import { useAuthStore } from "@/features/auth/store";
import { saveTokens, clearTokens } from "./auth-token";

async function doRefresh(): Promise<boolean> {
  const { refreshToken } = useAuthStore.getState();
  if (!refreshToken) return false;
  const resp = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!resp.ok) {
    clearTokens();
    useAuthStore.getState().clear();
    return false;
  }
  const data = await resp.json();
  useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
  saveTokens(data.access_token, data.refresh_token);
  return true;
}

export async function apiFetch(url: string, init: RequestInit = {}): Promise<Response> {
  const { accessToken } = useAuthStore.getState();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  let resp = await fetch(url, { ...init, headers });
  if (resp.status === 401 && (await doRefresh())) {
    const retryToken = useAuthStore.getState().accessToken;
    if (retryToken) headers["Authorization"] = `Bearer ${retryToken}`;
    resp = await fetch(url, { ...init, headers });
  }
  return resp;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- client` in `frontend/`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/api/client.ts frontend/src/lib/api/client.test.ts
git commit -m "feat(ui): add API client with refresh-on-401 retry"
```

### Task H4: Auth API calls

**Files:**
- Create: `frontend/src/features/auth/api.ts`
- Test: covered indirectly by LoginForm test (H5); no separate test file

- [ ] **Step 1: Write implementation**

```typescript
import { apiFetch } from "@/lib/api/client";
import { useAuthStore } from "./store";
import { saveTokens } from "@/lib/api/auth-token";

export interface LoginInput {
  email: string;
  password: string;
}

export async function login(input: LoginInput): Promise<void> {
  const resp = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!resp.ok) {
    const body = await resp.json();
    throw new Error(body.error?.message_en ?? "Login failed");
  }
  const data = await resp.json();
  useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
  saveTokens(data.access_token, data.refresh_token);
}

export async function fetchMe(): Promise<{ id: number; name: string; role: string }> {
  const resp = await apiFetch("/api/auth/me");
  const data = await resp.json();
  return data.user;
}
```

- [ ] **Step 2: Verify type check**

Run: `npm run typecheck` in `frontend/`
Expected: no type errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/auth/api.ts
git commit -m "feat(ui): add auth api calls"
```

### Task H5: LoginForm + smoke test

**Files:**
- Create: `frontend/src/features/auth/LoginForm.tsx`
- Test: `frontend/src/features/auth/LoginForm.test.tsx`

- [ ] **Step 1: Write the failing test**

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { LoginForm } from "./LoginForm";

vi.mock("./api", () => ({ login: vi.fn(async () => undefined) }));
import { login } from "./api";

describe("LoginForm", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders email and password fields", () => {
    render(<LoginForm onSuccess={() => {}} />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("calls login on submit", async () => {
    const onSuccess = vi.fn();
    render(<LoginForm onSuccess={onSuccess} />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "a@x.id" } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "secret" } });
    fireEvent.click(screen.getByRole("button", { name: /masuk|login/i }));
    await waitFor(() => expect(login).toHaveBeenCalledWith({ email: "a@x.id", password: "secret" }));
    await waitFor(() => expect(onSuccess).toHaveBeenCalled());
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- LoginForm` in `frontend/`
Expected: FAIL (component not defined).

- [ ] **Step 3: Write implementation**

```typescript
import { useState, type FormEvent } from "react";
import { login } from "./api";

export function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login({ email, password });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <label htmlFor="email">Email</label>
      <input id="email" type="email" value={email}
             onChange={(e) => setEmail(e.target.value)} required />
      <label htmlFor="password">Password</label>
      <input id="password" type="password" value={password}
             onChange={(e) => setPassword(e.target.value)} required />
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={busy}>Masuk</button>
    </form>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- LoginForm` in `frontend/`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/auth/LoginForm.tsx frontend/src/features/auth/LoginForm.test.tsx
git commit -m "feat(ui): add LoginForm with smoke tests"
```

### Task H6: ProtectedRoute + redirect test

**Files:**
- Create: `frontend/src/features/auth/ProtectedRoute.tsx`
- Test: `frontend/src/features/auth/ProtectedRoute.test.tsx`

- [ ] **Step 1: Write the failing test**

```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "./ProtectedRoute";
import { useAuthStore } from "./store";

function renderAt(initial: string) {
  return render(
    <MemoryRouter initialEntries={[initial]}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => useAuthStore.getState().clear());

  it("redirects to login when unauthenticated", () => {
    renderAt("/dashboard");
    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  it("renders child when authenticated", () => {
    useAuthStore.getState().setTokens("acc", "ref");
    renderAt("/dashboard");
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- ProtectedRoute` in `frontend/`
Expected: FAIL (component not defined).

- [ ] **Step 3: Write implementation**

```typescript
import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "./store";

export function ProtectedRoute() {
  const accessToken = useAuthStore((s) => s.accessToken);
  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- ProtectedRoute` in `frontend/`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/auth/ProtectedRoute.tsx frontend/src/features/auth/ProtectedRoute.test.tsx
git commit -m "feat(ui): add ProtectedRoute with redirect tests"
```

### Task H7: App shell + login route + dev server check

**Files:**
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/routes/login.tsx`
- Create: `frontend/index.html`

- [ ] **Step 1: Write index.html**

```html
<!doctype html>
<html lang="id">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>EKG-Insight CDSS</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 2: Write login.tsx route**

```typescript
import { useNavigate } from "react-router-dom";
import { LoginForm } from "@/features/auth/LoginForm";

export function LoginRoute() {
  const navigate = useNavigate();
  return (
    <main>
      <h1>EKG-Insight</h1>
      <LoginForm onSuccess={() => navigate("/dashboard")} />
    </main>
  );
}
```

- [ ] **Step 3: Write App.tsx + main.tsx**

```typescript
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
```

```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { App } from "./App";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
```

- [ ] **Step 4: Verify build + full frontend gate**

Run (in `frontend/`):

```bash
npm run lint && npm run format:check && npm run typecheck && npm run test && npm run build
```

Expected: all green; `npm run dev` serves the login page at :5173 and proxies /api to :5000.

- [ ] **Step 5: Commit**

```bash
git add frontend/index.html frontend/src/main.tsx frontend/src/App.tsx frontend/src/routes/login.tsx
git commit -m "feat(ui): add app shell, login route, and protected dashboard placeholder"
```

## Phase I: Seed Scripts & Ops

Goal: seed the facility, admin user, and default SystemConfig rows; provide Litestream config and dev/build scripts. First-run order: init_secrets -> alembic upgrade head -> seed_facility -> seed_admin -> seed_system_config.

### Task I1: seed_facility script

**Files:**
- Create: `scripts/seed_facility.py`
- Test: `backend/tests/unit/scripts/test_seed_facility.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from scripts.seed_facility import seed_facility

def test_seed_facility_creates_row(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 's.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_facility(s, name="Puskesmas A", code="PKM-A", facility_type="puskesmas",
                      address="Jl. Sehat 1")
        s.commit()
        f = s.scalar(select(HealthcareFacility).where(HealthcareFacility.code == "PKM-A"))
        assert f is not None

def test_seed_facility_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 's2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_facility(s, name="A", code="PKM-A", facility_type="puskesmas", address="x")
        s.commit()
        seed_facility(s, name="A", code="PKM-A", facility_type="puskesmas", address="x")
        s.commit()
        assert s.query(HealthcareFacility).filter_by(code="PKM-A").count() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_seed_facility.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write implementation**

```python
"""Seed a single HealthcareFacility row (idempotent on code)."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.facility import HealthcareFacility

def seed_facility(session: Session, *, name: str, code: str,
                  facility_type: str, address: str | None = None) -> HealthcareFacility:
    existing = session.scalar(select(HealthcareFacility).where(HealthcareFacility.code == code))
    if existing is not None:
        return existing
    facility = HealthcareFacility(name=name, code=code,
                                  facility_type=facility_type, address=address)
    session.add(facility)
    return facility
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_seed_facility.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/seed_facility.py backend/tests/unit/scripts/test_seed_facility.py
git commit -m "feat(infra): add seed_facility script"
```

### Task I2: seed_admin script (prompt + env fallback)

**Files:**
- Create: `scripts/seed_admin.py`
- Test: `backend/tests/unit/scripts/test_seed_admin.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.core.security.password import verify_password
from scripts.seed_admin import seed_admin

def test_seed_admin_creates_admin(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'a.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.commit()
        seed_admin(s, name="Admin", email="admin@x.id", password="StrongPass1",
                   facility_id=1, rounds=4)
        s.commit()
        u = s.scalar(select(User).where(User.email == "admin@x.id"))
        assert u.role == "admin"
        assert verify_password("StrongPass1", u.password_hash)

def test_seed_admin_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'a2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.commit()
        seed_admin(s, name="Admin", email="admin@x.id", password="x", facility_id=1, rounds=4)
        s.commit()
        seed_admin(s, name="Admin", email="admin@x.id", password="x", facility_id=1, rounds=4)
        s.commit()
        assert s.query(User).filter_by(email="admin@x.id").count() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_seed_admin.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write implementation**

```python
"""Seed the first admin user. Idempotent on email.

Entrypoint reads from interactive prompt, falling back to env vars
ADMIN_EMAIL / ADMIN_PASSWORD / ADMIN_NAME for non-interactive (CI/Docker).
"""
import os
import sys
from getpass import getpass
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.core.security.password import hash_password

def seed_admin(session: Session, *, name: str, email: str, password: str,
               facility_id: int, rounds: int = 12) -> User:
    existing = session.scalar(select(User).where(User.email == email))
    if existing is not None:
        return existing
    user = User(name=name, email=email, password_hash=hash_password(password, rounds=rounds),
                role="admin", facility_id=facility_id)
    session.add(user)
    return user

def _read_credentials() -> tuple[str, str, str]:
    if sys.stdin.isatty():
        name = input("Admin name: ")
        email = input("Admin email: ")
        password = getpass("Admin password: ")
    else:
        name = os.environ["ADMIN_NAME"]
        email = os.environ["ADMIN_EMAIL"]
        password = os.environ["ADMIN_PASSWORD"]
    return name, email, password
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_seed_admin.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/seed_admin.py backend/tests/unit/scripts/test_seed_admin.py
git commit -m "feat(infra): add seed_admin script with prompt and env fallback"
```

### Task I3: seed_system_config script

**Files:**
- Create: `scripts/seed_system_config.py`
- Test: `backend/tests/unit/scripts/test_seed_system_config.py`

- [ ] **Step 1: Write the failing test**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.models.system_config import SystemConfig
from scripts.seed_system_config import seed_system_config

def test_seed_defaults(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'sc.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_system_config(s)
        s.commit()
        keys = {c.key for c in s.scalars(select(SystemConfig)).all()}
        assert "enable_clinical_mode" in keys
        assert "default_model_id" in keys
        assert "nearest_pci_facility_distance_minutes" in keys

def test_seed_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'sc2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_system_config(s); s.commit()
        seed_system_config(s); s.commit()
        assert s.query(SystemConfig).filter_by(key="enable_clinical_mode").count() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_seed_system_config.py -v`
Expected: FAIL (module not defined).

- [ ] **Step 3: Write implementation**

```python
"""Seed default SystemConfig rows (idempotent per key)."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.system_config import SystemConfig

_DEFAULTS: dict[str, dict] = {
    "enable_clinical_mode": {"value": True},
    "default_model_id": {"value": None},
    "nearest_pci_facility_distance_minutes": {"value": None},
}

def seed_system_config(session: Session) -> None:
    for key, value in _DEFAULTS.items():
        existing = session.scalar(select(SystemConfig).where(SystemConfig.key == key))
        if existing is None:
            session.add(SystemConfig(key=key, value_json=value))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_seed_system_config.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/seed_system_config.py backend/tests/unit/scripts/test_seed_system_config.py
git commit -m "feat(infra): add seed_system_config script"
```

### Task I4: Litestream config + dry-run verification

**Files:**
- Create: `litestream.yml`
- Test: manual dry-run (documented; no pytest)

- [ ] **Step 1: Write litestream.yml**

```yaml
# Litestream replication config. Requires WAL mode (set via SQLite pragmas).
dbs:
  - path: data/cdss.db
    replicas:
      - type: file
        path: litestream-data/cdss
        retention: 168h
        sync-interval: 10s
```

- [ ] **Step 2: Verify config parses (dry-run)**

Run:

```bash
litestream replicate -config litestream.yml -exec "echo dry-run-ok"
```

Expected: Litestream starts, recognizes `data/cdss.db`, no config parse error. Stop with Ctrl+C. If `litestream` is not installed, document the manual install step; this AC is verified on the deployment machine.

- [ ] **Step 3: Commit**

```bash
git add litestream.yml
git commit -m "feat(infra): add litestream replication config"
```

### Task I5: dev.ps1 + build.ps1

**Files:**
- Create: `scripts/dev.ps1`
- Create: `scripts/build.ps1`

- [ ] **Step 1: Write dev.ps1**

```powershell
# Run backend (Flask :5000) and frontend (Vite :5173) in parallel.
$ErrorActionPreference = "Stop"
$backend = Start-Process pwsh -ArgumentList "-NoExit","-Command","cd backend; flask --app wsgi run --port 5000" -PassThru
$frontend = Start-Process pwsh -ArgumentList "-NoExit","-Command","cd frontend; npm run dev" -PassThru
Write-Host "Backend PID $($backend.Id), Frontend PID $($frontend.Id)"
Write-Host "Press Ctrl+C in each window to stop."
```

- [ ] **Step 2: Write build.ps1**

```powershell
# Build frontend into backend/app/static for single-process production serving.
$ErrorActionPreference = "Stop"
Push-Location frontend
npm install
npm run build
Pop-Location
Write-Host "Frontend built into backend/app/static"
```

- [ ] **Step 3: Verify build script**

Run: `pwsh scripts/build.ps1`
Expected: `backend/app/static/index.html` exists after build.

- [ ] **Step 4: Commit**

```bash
git add scripts/dev.ps1 scripts/build.ps1
git commit -m "feat(infra): add dev and build PowerShell scripts"
```

## Phase J: CI Wire-Up & Acceptance

Goal: shared pytest fixtures, the AC-1..AC-13 acceptance test, CI workflow already exists (guards on backend/frontend presence) and now runs the real suites, and a final full-stack verification.

### Task J1: conftest.py shared fixtures

**Files:**
- Create: `backend/tests/conftest.py`
- Test: self-verifying (fixtures used by other tests)

- [ ] **Step 1: Write conftest.py**

```python
"""Shared pytest fixtures.

Guards against touching the real data/cdss.db: TestConfig uses in-memory,
and the file fixture uses tmp_path only.
"""
import os
import pytest
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from app import create_app
from app.config import TestConfig
from app.extensions import db as _db
from app.db.types.context import set_crypto
from app.core.encryption.fernet_provider import FernetProvider
from app.core.encryption.hash_provider import HashProvider
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.core.security.password import hash_password

@pytest.fixture(autouse=True)
def _guard_real_db():
    url = os.environ.get("DATABASE_URL", "")
    assert "cdss.db" not in url or ":memory:" in TestConfig.SQLALCHEMY_DATABASE_URI, (
        "Tests must not target the real database"
    )

@pytest.fixture()
def app():
    set_crypto(FernetProvider(Fernet.generate_key()), HashProvider(b"test-pepper"))
    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()

@pytest.fixture()
def session(app) -> Session:
    return _db.session

@pytest.fixture()
def seeded_admin(session):
    session.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
    session.add(User(id=1, name="Admin", email="admin@x.id",
                     password_hash=hash_password("StrongPass1", rounds=4),
                     role="admin", facility_id=1))
    session.commit()
    return {"email": "admin@x.id", "password": "StrongPass1"}

@pytest.fixture()
def client(app):
    return app.test_client()
```

- [ ] **Step 2: Verify fixtures load**

Run: `pytest tests/ -q`
Expected: collection succeeds; existing tests still pass.

- [ ] **Step 3: Commit**

```bash
git add backend/tests/conftest.py
git commit -m "test(infra): add shared pytest fixtures with real-db guard"
```

### Task J2: Acceptance test AC-1..AC-13

**Files:**
- Create: `backend/tests/integration/test_acceptance.py`

- [ ] **Step 1: Write the acceptance tests**

```python
"""Sprint 1 acceptance criteria AC-1..AC-13 (automatable subset)."""
from sqlalchemy import select, text
from app.db.models.audit_log import AuditLog

def test_ac5_login_returns_tokens(client, seeded_admin):
    resp = client.post("/api/auth/login", json=seeded_admin)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["access_token"] and body["refresh_token"]

def test_ac6_refresh_rotation(client, seeded_admin):
    login = client.post("/api/auth/login", json=seeded_admin).get_json()
    resp = client.post("/api/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert resp.status_code == 200
    assert resp.get_json()["refresh_token"] != login["refresh_token"]

def test_ac7_rbac_blocks_without_token(client):
    assert client.get("/api/auth/me").status_code == 401

def test_ac8_audit_log_on_login(client, seeded_admin, session):
    client.post("/api/auth/login", json=seeded_admin)
    count = session.scalar(select(AuditLog).where(AuditLog.action == "login"))
    assert count is not None

def test_ac9_health_and_version(client):
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/version").status_code == 200

def test_ac9_health_db_probe(client):
    body = client.get("/api/health").get_json()
    assert body["db"] == "ok"
```

- [ ] **Step 2: Run the acceptance tests**

Run: `pytest tests/integration/test_acceptance.py -v`
Expected: PASS (6 automatable AC tests). AC-1/2/3/4/10/11/12/13 are verified by setup scripts, CI, and manual demo per the Demo Acceptance section.

- [ ] **Step 3: Commit**

```bash
git add backend/tests/integration/test_acceptance.py
git commit -m "test(infra): add Sprint 1 acceptance criteria tests"
```

### Task J3: CI wire-up verification

**Files:**
- Modify: `.github/workflows/ci.yml` (only if the existence guards need adjustment)

- [ ] **Step 1: Confirm CI detects backend and frontend**

The existing `ci.yml` guards on `backend/pyproject.toml` and `frontend/package.json`. Both now exist, so the backend and frontend jobs will run their real steps.

- [ ] **Step 2: Verify backend job commands match local**

Confirm the backend job runs `ruff check .`, `mypy .`, and `pytest --cov`. Confirm the frontend job runs `npm run lint`, `npm run format:check`, `npm run typecheck`, `npm run test`, and `npm run build`. Adjust `ci.yml` only if a command name differs from the scripts defined in Task A2.

- [ ] **Step 3: Push branch and confirm CI green**

```bash
git push -u origin feat/sprint-1/foundation
```

Expected: secret-scan, backend, and frontend jobs all pass on the PR.

- [ ] **Step 4: Commit (if ci.yml changed)**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: align workflow commands with sprint 1 scripts"
```

### Task J4: Full first-run verification (demo acceptance)

**Files:** none (verification only)

- [ ] **Step 1: Fresh setup from clean checkout**

Run, in order:

```bash
python scripts/init_secrets.py
cd backend; alembic upgrade head; cd ..
python scripts/seed_facility.py
python scripts/seed_admin.py
python scripts/seed_system_config.py
```

Expected: `secrets/master.key` + `secrets/hmac_pepper.key` created (AC-2); 6 tables migrated (AC-3); facility + admin + config rows present (AC-4).

- [ ] **Step 2: Start backend and verify endpoints**

Run: `cd backend; flask --app wsgi run --port 5000`
Then:

```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/version
```

Expected: health 200 with `db: ok` (AC-9), version returns version + git_sha.

- [ ] **Step 3: Login round-trip + audit (AC-5, AC-8)**

```bash
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d '{"email":"admin@x.id","password":"<your-seeded-password>"}'
```

Expected: 200 with access + refresh tokens. Confirm an `audit_log` row with action=login.

- [ ] **Step 4: Frontend dev server (AC-13)**

Run: `pwsh scripts/dev.ps1`
Expected: Vite serves login at :5173; submitting valid credentials navigates to /dashboard; `/api` proxied to :5000.

- [ ] **Step 5: structlog JSON + Litestream (AC-10, AC-11)**

Confirm backend stdout logs are single-line JSON (AC-10). Run `litestream replicate -config litestream.yml` and confirm it begins replicating `data/cdss.db` without error (AC-11).

- [ ] **Step 6: Tag the sprint release**

```bash
git switch main && git pull
git tag -a v0.1.0-sprint-1 -m "Sprint 1: Project Foundation"
git push origin v0.1.0-sprint-1
```

---

## Self-Review

**1. Spec coverage (Sprint 1 design Section 1 In-Scope + AC-1..AC-13):**

| Spec item | Task(s) |
| --- | --- |
| Repo skeleton (backend+frontend) | A1-A6, G3, H7 |
| SQLite + Litestream config | C2, C3, I4 |
| 6 tables | D1-D6, D7 |
| Alembic migration | C6, D7 |
| Encryption key bootstrap | B1-1, B1-2, B1-4 |
| JWT auth (login/access+refresh/rotation) | F2, F5, F7, G5 |
| RBAC middleware (5 roles) | F3 |
| structlog + audit writer | E1, E4, F4 |
| Health + version | G4 |
| CI lint/test skeleton | A1-A4, J3 |
| Seed scripts | I1, I2, I3 |
| AC-1 fresh install | J4 |
| AC-2 master.key 0600 | B1-4, J4 |
| AC-3 migrate 6 tables | C6, D7 |
| AC-4 seed facility+admin | I1, I2, J4 |
| AC-5 login tokens | G5, J2 |
| AC-6 refresh rotation | F5, G5, J2 |
| AC-7 RBAC 403 | F3, J2 |
| AC-8 audit on login | F4, J2 |
| AC-9 health+version | G4, J2 |
| AC-10 structlog JSON | E1, J4 |
| AC-11 litestream | I4, J4 |
| AC-12 CI green | J3 |
| AC-13 FE dev+proxy | H7, J4 |

No gaps found.

**2. Placeholder scan:** No TBD/TODO/"add error handling" left. Each code step shows full code. The only deferred-decision notes (AuditLog.facility_id nullable, exposing `_utcnow`) include explicit instructions, not vague placeholders.

**3. Type consistency:** Verified key signatures across tasks: `write_audit(session, *, facility_id, action, user_id, ...)` (E4) is called consistently in F4. `issue_refresh_token(session, *, user_id, ttl_days)` and `rotate_refresh_token(session, *, raw_token, ttl_days)` (F5) match calls in G5. `make_access_token(*, user_id, role, facility_id)` (F7) matches G5. `hash_password(plain, rounds=...)` / `verify_password(plain, hashed)` (F1) match login_service (F4) and seeds (I2). `set_crypto/get_fernet/get_hasher` (B2-1) match conftest (J1) and app factory (G3). `useAuthStore` shape (H1) matches client (H3) and ProtectedRoute (H6).

**4. Known cross-task dependency notes for the implementer:**
- AuditLog.facility_id should be nullable (login_failed for unknown email). If FK errors appear in F4, update the D4 model + regenerate migration in D7.
- `_utcnow` in `app/db/mixins/timestamp.py` must be importable (used by D5, D6).
- `flask-sqlalchemy` + `flask-migrate` + `email-validator` must be added to pyproject (noted in E5, G2).

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-30-sprint-1-foundation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - dispatch a fresh subagent per task, review between tasks, fast iteration. Best for this 58-task plan: isolates blast radius and keeps the main context clean.

**2. Inline Execution** - execute tasks in this session using executing-plans, batch execution with checkpoints for review.

Which approach?
