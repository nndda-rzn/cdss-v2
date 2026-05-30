# ADR-0001: Flask over FastAPI for backend

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: architecture-overview-design.md

## Context

The backend must run YOLO inference (PyTorch + Ultralytics) and HiResCAM, serve a REST API, and remain lightweight for CPU-only, offline-capable deployment in low-resource primary/remote facilities. The developer is already familiar with the chosen stack.

## Decision

Use Flask as the web framework, paired with SQLAlchemy 2.0, Alembic, and Pydantic for validation.

## Options Considered

### Option A - Flask
- Pros: Lightweight, mature, huge ecosystem, simple sync model fits PyTorch worker pattern, developer familiarity, easy local deployment.
- Cons: Async not first-class; must assemble auth/validation from extensions.

### Option B - FastAPI
- Pros: Async-native, auto OpenAPI, Pydantic built-in.
- Cons: Async adds little for CPU-bound inference; heavier mental model for long-running inference; not the developer's preferred stack.

### Option C - Django + DRF
- Pros: Batteries included (admin, auth, ORM).
- Cons: Heavyweight for a prototype; admin panel not suited to custom research dashboards.

## Consequences

- Positive: Minimal footprint, simple deployment, fits low-resource goals and developer skills.
- Negative: Manual wiring of JWT, validation, OpenAPI (mitigated by extensions).
- Risks: Sync blocking on long inference; mitigated by request-scoped workers and acceptable inference time targets.

## Notes

Aligns with PRD low-resource readiness requirements.
