# ADR-0006: RBAC with five roles

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: data-model-and-phi-design.md (RBAC matrix)

## Context

The system serves multiple actor types in a primary/remote facility: physicians, nurses, researchers, system admins, and cardiologist reviewers (Sp.JP) for Phase 2 rule validation. Access to PHI and clinical actions must be scoped.

## Decision

Define five roles: `admin`, `clinician`, `nurse`, `researcher`, `expert_reviewer`. Enforce via a `@require_role` decorator and a documented RBAC matrix.

## Options Considered

### Option A - Five roles (chosen)
- Pros: Clear separation; nurse handles registration/vitals/upload, clinician adds interpretation/disposition, researcher gets anonymized dashboards, expert_reviewer for Sp.JP co-design.
- Cons: Slightly more authorization code and tests.

### Option B - Four roles (merge nurse into clinician)
- Pros: Simpler.
- Cons: Loses the real workflow distinction between nurse data entry and clinician decision-making.

### Option C - Three roles
- Pros: Minimal.
- Cons: Expert reviewer via a flag is awkward; weaker audit clarity.

## Consequences

- Positive: Matches real clinical workflow; supports PHI access policies and audit clarity.
- Negative: More permission combinations to test.
- Risks: Role creep; mitigated by a single source-of-truth RBAC matrix.

## Notes

`expert_reviewer` is largely dormant in Phase 1, active in Phase 2 co-design.
