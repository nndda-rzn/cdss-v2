# ADR-0011: Clinical-sharp border radius

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: color-system-and-tokens-design.md

## Context

Default UI kits (including shadcn/ui) tend toward 8-12px rounded corners, producing a consumer/SaaS feel. Real medical documents and physical triage tags are rectangular with minimal radius.

## Decision

Use a clinical-sharp radius scale: 0 / 1 / 2 / 3 / 4 / 6px, plus `full` for circular avatars/icons only. Default component radius is 2px. Triage and risk badges are rectangular (2px), not pills.

## Options Considered

### Option A - Clinical-sharp (chosen)
- Pros: Instrument-grade, documentary feel; triage badges resemble physical ER tags; clearly distinct from generic templates.
- Cons: Can feel austere if combined with cold neutrals (mitigated by warm-tinted charcoal + humane typography).

### Option B - Default rounded (8-12px)
- Pros: Familiar, friendly.
- Cons: Consumer feel; less medical authority; generic.

## Consequences

- Positive: Distinctive, professional; rectangular badges read as signals, not decoration.
- Negative: Requires consistent application across components.
- Risks: Over-sharp starkness; mitigated by max 6px and warm neutrals.

## Notes

Pill shape (full radius) is forbidden for badge/triage/status.
