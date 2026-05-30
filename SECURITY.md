# Security Policy

## Scope and Status

EKG-Insight CDSS is a **research prototype**, not a certified medical device. It handles Patient Health Information (PHI) and must follow data protection practices aligned with Indonesian UU PDP No. 27/2022 (health data = specific personal data requiring strict protection).

## Reporting a Vulnerability

Do **not** open a public issue for security vulnerabilities.

1. Email the maintainer privately (contact in repository About section).
2. Include: description, reproduction steps, affected component, potential impact.
3. Do **not** include real patient data in any report.
4. Expect acknowledgement within 7 days.

## PHI Handling Posture

### Data Tier Classification

| Tier | Examples | Treatment |
| --- | --- | --- |
| T1 Direct identifier | name, phone, address, full NIK | Encrypted at rest (Fernet), masked in UI |
| T2 Quasi-identifier | DOB, gender, MRN, NIK last-4 | Plaintext + RBAC + access log |
| T3 Hash-only | full NIK (for dedup) | HMAC-SHA256, irreversible |
| T4 Clinical context | vitals, symptoms | Plaintext (anonymous alone) |
| T5 System metadata | timestamps, IDs | Plaintext |

### Encryption

- Field-level encryption via `cryptography` Fernet (AES-128-CBC + HMAC).
- Master key in `secrets/master.key` (mode 0600), generated at first-run.
- Key **never** committed to git, **never** stored in DB.
- Key backed up separately from database backups.

### Access Control

- RBAC with 5 roles (admin, clinician, nurse, researcher, expert_reviewer).
- Every T1 field decryption logged to `phi_access_log`.
- JWT access token TTL 30 minutes; refresh token rotation.
- UI masks identifiers by default; full reveal is logged.

## Never Commit

The following are gitignored and must NEVER be committed:

- `secrets/` (master key, pepper)
- `data/` (SQLite DB with PHI)
- `storage/` (ECG images, heatmaps, reports)
- `models/**/*.pt` (model weights, hosted externally)
- `.env` files (credentials, JWT secret)
- Any real patient data

## Secret Scanning

- `gitleaks` runs in CI on every PR and push.
- If a secret is accidentally committed: rotate it immediately, do not just delete the commit.

## Forbidden System Output

The system must never produce: final diagnosis, treatment instructions, drug prescriptions/doses, invasive procedure decisions, or statements of certainty about disease presence/absence. See PRD Section 18.

## Dependency Security

- `dependabot` weekly updates for pip and npm.
- `pip-audit` and `npm audit` run in CI.
- Pin dependency versions; review unusual or typosquatting-like package names.
