# ADR-0014: Decision tree vs triage engine split

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: decision-engine-design.md, reference/01_Rule_Based_Design_source.md

## Context

Phase 1 (classification-based) uses a Decision Tree (DT-01..DT-10) producing a risk_level. Phase 2 (detection-based) uses a Rule-Based Triage Engine (R1-R17) producing a triage_level + class_4, and requires YOLO detection, bounding boxes, lead location, and Sp.JP annotation. Phase 2 is dormant until annotation exists.

## Decision

Implement two engines behind a stable public API `recommendation.generate(ctx)`: `decision_tree_engine` (active, Phase 1) and `triage_engine` (dormant, Phase 2, schema-ready). The Recommendation entity carries both `risk_level` (nullable) and `triage_level` (nullable) plus bilingual fields and `rules_fired_json`.

## Options Considered

### Option A - Two engines, one stable API (chosen)
- Pros: Clean separation; Phase 2 can be enabled without frontend changes; transparent audit (rules fired); each engine independently testable.
- Cons: Two engine implementations and a small orchestrator.

### Option B - Single engine overloaded for both phases
- Pros: Less code initially.
- Cons: Mixed responsibilities; risk_level and triage_level conflated; harder to audit and test.

## Consequences

- Positive: Future-proof toward Phase 2; one-file-per-rule granularity (DT-01.., R1..); clear conflict resolution (RED>YELLOW>GREEN; risk hierarchy in Phase 1).
- Negative: Two engines to maintain.
- Risks: Divergent output shapes; mitigated by a common Recommendation DTO with separate, well-defined level fields.

## Notes

Phase 2 rules require cardiologist co-design and sign-off (ExpertReview, Sprint 9).
