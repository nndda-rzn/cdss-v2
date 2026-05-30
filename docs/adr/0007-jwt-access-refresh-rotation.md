# ADR-0007: JWT access + refresh rotation

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: sprint-1-foundation-design.md

## Context

Authentication must work on unstable connections in remote facilities while limiting token replay risk. Sessions should recover quickly after power/network interruptions.

## Decision

Use JWT with a short-lived access token (30 minutes) and a refresh token (7 days) that rotates on each use. The refresh token hash is stored server-side for revocation.

## Options Considered

### Option A - Access + rotating refresh (chosen)
- Pros: Short access TTL limits exposure; rotation detects reuse; quick re-issue suits flaky connectivity; revocation via stored hash.
- Cons: Refresh rotation logic + storage to implement.

### Option B - Single long-lived token
- Pros: Simplest.
- Cons: Larger exposure window if leaked; forced re-auth on expiry.

### Option C - Server-side session cookie
- Pros: No refresh logic.
- Cons: Sticky-session concerns; less suited to SPA + API separation.

## Consequences

- Positive: Good security/usability balance for the target environment.
- Negative: Extra implementation and tests.
- Risks: Clock skew on offline devices; mitigated by reasonable leeway.

## Notes

Logout revokes the stored refresh token hash.
