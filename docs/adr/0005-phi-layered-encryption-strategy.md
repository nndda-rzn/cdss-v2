# ADR-0005: Layered PHI encryption strategy

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: data-model-and-phi-design.md, SECURITY.md

## Context

The system stores Patient Health Information and must comply with Indonesian UU PDP No. 27/2022 (health data = specific personal data). Facilities have minimal IT staff and no budget for HSM or commercial encryption. The storage stack (SQLite + Litestream) precludes SQLCipher.

## Decision

Adopt a five-layer strategy: (1) tier classification T1-T5; (2) application-level field encryption (Fernet) for T1 direct identifiers and HMAC-SHA256 for T3 hash-only fields, via SQLAlchemy TypeDecorators; (3) RBAC + PHIAccessLog + UI masking; (4) anonymous research export excluding T1/T3; (5) optional OS disk encryption in the runbook.

## Options Considered

### Option A - Layered field encryption (chosen)
- Pros: Litestream-compatible (SQLite format unchanged), granular, portable master key, low dependency footprint (`cryptography` only).
- Cons: Encrypted fields not directly searchable; key management is an ops responsibility.

### Option B - SQLCipher (full DB encryption)
- Pros: Transparent to app.
- Cons: Incompatible with Litestream raw access; special DB tooling needed.

### Option C - Plaintext + OS disk encryption only
- Pros: Simplest.
- Cons: Backups unprotected; fails on stolen DB file.

## Consequences

- Positive: PHI protected at rest and in backups; standard tools still open the DB (only T1 columns unreadable without key).
- Negative: Search by name requires hashing/derivation; key lifecycle must be documented.
- Risks: Key compromise; mitigated by rotation + re-encrypt batch and separate key backup.

## Notes

Master key in `secrets/master.key` (0600), never committed, never in DB.
