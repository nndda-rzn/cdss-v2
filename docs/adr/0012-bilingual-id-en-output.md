# ADR-0012: Bilingual ID + EN output

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: decision-engine-design.md

## Context

The product serves Indonesian healthcare staff (PRD language: id), while the research targets Scopus Q2/Q3 (international audience). The rule-based design already specifies bilingual rationale and recommended actions.

## Decision

Store and present rationale, recommended action, and error messages in both Indonesian (id) and English (en). UI defaults to Indonesian with a language toggle. DB carries paired columns (`*_id`, `*_en`); DecisionRule carries paired templates.

## Options Considered

### Option A - Bilingual ID + EN (chosen)
- Pros: Serves local staff and international reviewers; modest effort (paired columns/templates); extra selling point for publication.
- Cons: Two-language content maintenance.

### Option B - ID only
- Pros: Simplest; matches local audience.
- Cons: Harder for Scopus reviewers; limits international reach.

### Option C - EN only
- Pros: Standard for GitHub/Scopus.
- Cons: Contradicts the Indonesian primary-care audience.

## Consequences

- Positive: Broader reach; clinical output and errors localized; defensible internationalization story.
- Negative: Translation upkeep for templates and messages.
- Risks: Drift between languages; mitigated by centralizing templates and i18n loader.

## Notes

Clinical text is not PHI and is stored plaintext.
