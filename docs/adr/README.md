# Architecture Decision Records

This directory records significant architecture decisions for EKG-Insight CDSS using the [Nygard ADR format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

## Why ADRs

For a research project targeting Scopus Q2/Q3 publication, ADRs provide methodological traceability: reviewers see the rationale for each choice as it was made, not reconstructed post-hoc. They form a strong appendix for the thesis methodology chapter.

## Process

1. Propose a decision via the `adr_proposal` issue template.
2. Discuss options and consequences.
3. When accepted, copy `_template.md` to `NNNN-short-title.md` (next number).
4. Set status to Accepted and link the implementing PR.
5. If a later decision overrides this one, set status to Superseded and link the new ADR.

## Status Values

- **Proposed** - under discussion
- **Accepted** - decided and in effect
- **Superseded** - replaced by a later ADR
- **Deprecated** - no longer relevant

## Index

| ADR | Title | Status |
| --- | --- | --- |
| [0001](0001-flask-over-fastapi.md) | Flask over FastAPI for backend | Accepted |
| [0002](0002-sqlite-with-litestream.md) | SQLite with Litestream for storage | Accepted |
| [0003](0003-monorepo-unified-deployable.md) | Monorepo, unified deployable | Accepted |
| [0004](0004-three-yolo-models-comparison.md) | Multiple YOLO models for comparison (3->5) | Accepted |
| [0005](0005-phi-layered-encryption-strategy.md) | Layered PHI encryption strategy | Accepted |
| [0006](0006-rbac-five-roles.md) | RBAC with five roles | Accepted |
| [0007](0007-jwt-access-refresh-rotation.md) | JWT access + refresh rotation | Accepted |
| [0008](0008-encounter-driven-ai-only-workflow.md) | Encounter-driven, AI-only workflow | Accepted |
| [0009](0009-22-table-clinical-schema.md) | 22-table clinical schema | Accepted |
| [0010](0010-petrol-charcoal-color-system.md) | Petrol + charcoal color system | Accepted |
| [0011](0011-clinical-sharp-radius.md) | Clinical-sharp border radius | Accepted |
| [0012](0012-bilingual-id-en-output.md) | Bilingual ID + EN output | Accepted |
| [0013](0013-inferno-heatmap-colormap.md) | Inferno heatmap colormap | Accepted |
| [0014](0014-decision-tree-vs-triage-engine-split.md) | Decision tree vs triage engine split | Accepted |
| [0015](0015-dedup-strategy.md) | Patient deduplication strategy | Accepted |
