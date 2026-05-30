# ADR-0002: SQLite with Litestream for storage

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: data-model-and-phi-design.md

## Context

Deployment targets primary/remote facilities with limited IT staff, unstable power and internet, and no budget for a managed database server. Data must be durable, backup-able, and recoverable, while supporting offline operation.

## Decision

Use SQLite as the primary database with Litestream for continuous WAL streaming backup to an external destination (when connectivity allows).

## Options Considered

### Option A - SQLite + Litestream
- Pros: Zero-config, single-file, ~10MB footprint, no server process, offline-native; Litestream gives forensic-grade WAL backup without blocking; portable for research reproducibility.
- Cons: Single-writer concurrency; requires WAL mode; field encryption needed for PHI.

### Option B - PostgreSQL
- Pros: Concurrency, rich features.
- Cons: Server process, ~100MB+ idle RAM, ops burden unsuitable for remote facilities.

### Option C - SQLite only (no replication)
- Pros: Simplest.
- Cons: No backup story; data loss risk on disk failure.

## Consequences

- Positive: Lowest operational complexity, offline-first, easy backup/restore by copying a file.
- Negative: Single-writer; must enable `PRAGMA journal_mode=WAL` and `foreign_keys=ON`.
- Risks: Backup destination availability; mitigated by async replication that tolerates intermittent connectivity.

## Notes

SQLCipher was rejected because it is incompatible with Litestream's raw access; PHI is instead protected by application-level field encryption (see ADR-0005).
