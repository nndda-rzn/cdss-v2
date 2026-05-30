# ADR-0008: Encounter-driven, AI-only workflow

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: data-model-and-phi-design.md

## Context

The system must feel like a real CDSS for a healthcare facility while staying within research scope. It is not a full HIS/SIMRS and must not manage labs, prescriptions, or billing.

## Decision

Adopt an encounter-driven workflow: a patient Encounter is created first as clinical context, then ECG upload and AI analysis occur within it. Scope is AI-only: the clinical output is a follow-up recommendation from the Rule-Based System + Decision Tree, not full clinical management.

## Options Considered

### Option A - Encounter-driven, AI-only (chosen)
- Pros: Realistic clinical context (chief complaint, vitals, history) feeds the decision engine (e.g. DT-10, R7); bounded scope avoids HIS creep.
- Cons: More entities than a pure upload tool (Patient, Encounter, ClinicalContext, VitalSigns).

### Option B - Upload-centric (AI-only entry)
- Pros: Lighter; patient/encounter created on the fly.
- Cons: Weak clinical context; poorer fit for MI assessment which needs symptoms and vitals.

## Consequences

- Positive: Clinically credible; supports context-aware recommendations and disposition tracking.
- Negative: Larger schema and more UI for registration/encounter.
- Risks: Scope creep toward HIS; mitigated by explicit out-of-scope list (no lab/prescription/billing).

## Notes

Output closes the loop with Disposition and optional Referral.
