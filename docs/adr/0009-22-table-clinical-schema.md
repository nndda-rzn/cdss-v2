# ADR-0009: 22-table clinical schema

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: data-model-and-phi-design.md

## Context

The original PRD schema (7 tables) treated each examination as standalone, unsuitable for a real CDSS where examinations belong to patients, encounters, and a facility. The system targets a deployable (research-grade) CDSS for a primary/remote facility.

## Decision

Adopt a 22-table operational schema spanning identity, patient, encounter, ECG & AI, decision, disposition, audit, config, and dormant Phase 2 domains. The PRD 7-table schema becomes a subset.

## Options Considered

### Option A - 22-table clinical schema (chosen)
- Pros: Realistic CDSS; separates ECGStudy / AIAnalysis / Recommendation / ClinicalInterpretation; supports multi-model analysis, PHI tiers, disposition/referral, and audit.
- Cons: 3x more tables; more migrations and tests.

### Option B - Minimal research schema (7 tables)
- Pros: Simplest.
- Cons: Cannot represent real clinical workflow; weak deployability narrative.

### Option C - Hybrid minimum (add Patient + Encounter only)
- Pros: Less work.
- Cons: Misses disposition, consent, PHI access logging; not a credible CDSS.

## Consequences

- Positive: Strong engineering novelty (deployable schema); clean separation of concerns; Phase 2 ready (dormant tables).
- Negative: More schema surface; additive migrations per sprint.
- Risks: Over-modeling; mitigated by AI-only scope (no lab/prescription/billing tables).

## Notes

ExpertReview and DetectionResult are created in Sprint 9.
