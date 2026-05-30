# Sprint 1 Foundation Design - EKG-Insight CDSS v2

| Item | Keterangan |
| --- | --- |
| Dokumen | Sprint 1 Foundation Design |
| Versi | 1.0 |
| Tanggal | 2026-05-30 |
| Status | Approved design - siap masuk implementation plan |
| Referensi | architecture-overview-design.md, data-model-and-phi-design.md |
| Scope | Tight Foundation |

## 1. Sprint 1 Scope

Tujuan: menyiapkan fondasi yang dapat di-install di mesin baru, dengan auth skeleton, encryption bootstrap, audit logging, dan CI. Belum ada workflow klinis (itu Sprint 2+).

### In Scope

1. Repository skeleton lengkap (backend + frontend folder structure).
2. SQLite + Litestream config.
3. 5 tabel: HealthcareFacility, User, AuditLog, PHIAccessLog, SystemConfig.
4. Alembic migration awal.
5. Encryption key bootstrap (`init_secrets.py`, Fernet key generation).
6. JWT auth skeleton (login, access + refresh token, rotation).
7. RBAC middleware (5 role decorator).
8. structlog config + audit log writer.
9. Health check + version endpoint.
10. CI lint/test skeleton (ruff, mypy, pytest, eslint, vitest).
11. Seed scripts (facility, admin user).

### Out of Scope (sprint berikutnya)

- Patient/Encounter management (Sprint 2)
- Upload + image quality (Sprint 2)
- AI inference (Sprint 3)
- HiResCAM, Decision Tree, History, PDF, Research dashboard (Sprint 4-7)

## 2. Acceptance Criteria

| # | Kriteria | Verifikasi |
| --- | --- | --- |
| AC-1 | Repo dapat di-clone + setup di mesin baru | `scripts/setup` selesai tanpa error |
| AC-2 | `init_secrets.py` generate master.key (mode 0600) | File ada, tidak ter-commit |
| AC-3 | Alembic migrate 5 tabel sukses | `alembic upgrade head` + cek schema |
| AC-4 | Seed facility + admin sukses | Row di DB, admin bisa login |
| AC-5 | Admin login -> dapat access + refresh token | POST /api/auth/login 200 |
| AC-6 | Refresh token rotation bekerja | POST /api/auth/refresh issue token baru |
| AC-7 | RBAC decorator menolak akses tidak sah | Request tanpa role -> 403 |
| AC-8 | Audit log tercatat saat login | Row di audit_log |
| AC-9 | Health + version endpoint | GET /api/health 200, /api/version return versi |
| AC-10 | structlog output JSON | Log stdout berformat JSON |
| AC-11 | Litestream config valid | `litestream replicate` jalan (dry-run) |
| AC-12 | CI lint+test pass | ruff, mypy, pytest, eslint, vitest hijau |
| AC-13 | Frontend dev server jalan + proxy /api | `npm run dev` + login page render |

## 3. Folder Skeleton (Sprint 1)

```
backend/
  app/
    __init__.py              # app factory create_app()
    config.py                # Config Dev/Prod/Test
    extensions.py            # db, jwt, migrate singletons
    api/
      __init__.py            # register_blueprints
      auth.py                # login/logout/refresh
      health.py              # health/version
    core/
      security/
        jwt.py
        password.py
        tokens.py
      rbac/
        roles.py
        decorators.py
      encryption/
        fernet_provider.py
        field_encryption.py
        hash_provider.py
        key_loader.py
      logging/
        config.py
        processors.py
      exceptions/
        base.py
        handlers.py
    db/
      base.py
      session.py
      engine.py
      pragmas.py
      mixins/
        timestamp.py
      types/
        encrypted_string.py
        hashed_string.py
      models/
        __init__.py
        facility.py
        user.py
        audit_log.py
        phi_access_log.py
        system_config.py
    schemas/
      auth.py
      common.py
    services/
      auth/
        login_service.py
        token_service.py
      audit/
        writer.py
  migrations/                # alembic
  tests/
    conftest.py
    unit/
    integration/
  pyproject.toml
  alembic.ini
  wsgi.py
frontend/
  src/
    main.tsx
    App.tsx
    routes/
      login.tsx
    features/
      auth/
        api.ts
        store.ts
        LoginForm.tsx
        ProtectedRoute.tsx
    lib/
      api/
        client.ts
        auth-token.ts
    components/
      ui/
  package.json
  vite.config.ts
  tsconfig.json
```

## 4. Migrasi Tabel Sprint 1

5 tabel (detail field di data-model doc Section 4):

| Tabel | Sprint 1 Notes |
| --- | --- |
| HealthcareFacility | Seeded 1 row saat install |
| User | Admin pertama via seed; password bcrypt |
| AuditLog | Writer aktif sejak login pertama |
| PHIAccessLog | Tabel + writer ada; belum dipanggil sampai Patient aktif (Sprint 2) |
| SystemConfig | Key-value config global faskes |

SQLite pragma diaktifkan: `PRAGMA foreign_keys=ON`, `PRAGMA journal_mode=WAL` (wajib untuk Litestream).

## 5. Bootstrap Scripts

| Script | Fungsi |
| --- | --- |
| scripts/init_secrets.py | Generate Fernet master key -> secrets/master.key (0600) + HMAC pepper |
| scripts/seed_facility.py | Input nama/kode/tipe/alamat faskes -> 1 row HealthcareFacility |
| scripts/seed_admin.py | Input email/password admin -> 1 row User role=admin |
| scripts/dev.ps1 | Jalankan backend (Flask :5000) + frontend (Vite :5173) paralel |
| scripts/build.ps1 | npm run build -> copy ke backend/app/static |

Urutan first-run: init_secrets -> alembic upgrade head -> seed_facility -> seed_admin.

## 6. Endpoint Spec Sprint 1

| Endpoint | Method | Auth | Response |
| --- | --- | --- | --- |
| /api/health | GET | none | `{status: "ok", db: "ok", time}` |
| /api/version | GET | none | `{version, build, git_sha}` |
| /api/auth/login | POST | none | `{access_token, refresh_token, user}` |
| /api/auth/refresh | POST | refresh token | `{access_token, refresh_token}` (rotate) |
| /api/auth/logout | POST | access token | `{status: "ok"}` (revoke refresh) |
| /api/auth/me | GET | access token | `{user: {id, name, role, facility}}` |

### JWT Strategy

| Token | TTL | Catatan |
| --- | --- | --- |
| Access | 30 menit | Bearer header |
| Refresh | 7 hari | Rotate on use; hash disimpan di DB untuk revoke |

## 7. Error Handling Format

Structured response konsisten untuk semua endpoint:

```json
{
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message_id": "Email atau password salah",
    "message_en": "Invalid email or password",
    "field": "credentials",
    "request_id": "uuid-correlation-id"
  }
}
```

| Aturan | Detail |
| --- | --- |
| code | String enum stabil (untuk i18n + frontend mapping) |
| message_id/en | Bilingual; UI pilih sesuai locale |
| request_id | Correlation ID, ikut tercatat di audit log |
| HTTP status | 400/401/403/404/409/422/500 sesuai jenis |

Exception hierarchy: AppException -> AuthError/ValidationError/NotFoundError/ConflictError. Handler global map ke format di atas.

## 8. Audit Logging

| Aspek | Detail |
| --- | --- |
| Library | structlog -> JSON stdout + file |
| Trigger Sprint 1 | login, logout, refresh, failed login |
| Field | user_id, facility_id, action, entity, ip, user_agent, request_id, created_at |
| Writer | services/audit/writer.py dipanggil dari service layer (bukan middleware tersembunyi) |

## 9. CI / Quality Skeleton

| Tool | Target |
| --- | --- |
| ruff | Lint Python |
| mypy | Type check Python |
| pytest | Unit + integration backend |
| eslint | Lint TypeScript |
| prettier | Format check |
| vitest | Unit frontend |
| pre-commit | Hook lokal jalankan ruff + eslint + format |

CI pipeline (GitHub Actions atau lokal): install deps -> lint -> type check -> test -> report.

## 10. Demo Acceptance Sprint 1

"Instance dapat di-install di mesin baru: jalankan init_secrets -> migrate -> seed -> admin login -> audit log tercatat -> health/version endpoint hijau. Instance siap menerima implementasi Sprint 2 (Patient/Encounter + Upload)."

## 11. Transisi ke Implementation Plan

Setelah design ini disetujui, invoke writing-plans skill untuk menyusun implementation plan Sprint 1 (langkah TDD per komponen). Sprint 2-9 mendapat design + plan masing-masing saat tiba gilirannya.
