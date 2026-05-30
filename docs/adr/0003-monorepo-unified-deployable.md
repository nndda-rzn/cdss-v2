# ADR-0003: Monorepo, unified deployable

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: architecture-overview-design.md

## Context

The project has a Flask backend and a React frontend, plus model artifacts, runtime storage, and documentation. It is a solo-developer thesis project that must be easy to demo and deploy on a single machine.

## Decision

Use a monorepo with `backend/` and `frontend/` subfolders. In production, the frontend builds into `backend/app/static/` so a single Flask process serves the app (unified deployable). In development, Vite runs separately and proxies `/api` to Flask.

## Options Considered

### Option A - Monorepo, unified deployable
- Pros: One repo, synced FE/BE versions per commit, single demo URL, low deployment friction, easy for one developer.
- Cons: Two toolchains (pip + npm); build step copies frontend into backend static.

### Option B - Two repositories
- Pros: Independent ownership.
- Cons: Version drift, CORS setup, double overhead; overkill for solo.

### Option C - Git submodule
- Pros: Shared frontend reuse.
- Cons: Submodule friction; no benefit here.

## Consequences

- Positive: Simplest dev and demo experience; single deployable artifact for low-resource sites.
- Negative: Build script must copy frontend output; both toolchains installed for full dev.
- Risks: Coupling; mitigated by clear folder boundaries and API contract.

## Notes

Dev uses two terminals; production uses one process.
