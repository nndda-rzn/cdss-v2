# Pull Request Flow

Even as a solo developer, every change goes through a PR. This builds an evidence trail for the thesis defense and Scopus review, enables CI gates, and keeps history discoverable.

## Why PR for Solo Dev

- PR description = mini design rationale (defendable in defense).
- CI auto-enforces quality before merge.
- Searchable history ("when did encryption land?").
- Reviewers can trace system evolution.

## Lifecycle

```
1. Branch from main
2. Conventional commits
3. Push, open PR (template auto-loads)
4. CI runs: secret-scan, backend lint/type/test, frontend lint/type/test/build
5. Self-review after cooldown
6. Address own comments
7. Squash merge to main
8. Delete branch
```

## Cooldown Rule

For changes labeled `size/m` or larger, wait at least **24 hours** before self-merging. Fresh eyes catch bugs, leaked secrets, and missed edge cases. Small changes (`size/xs`, `size/s`) may merge same-day after CI passes.

## Self-Review Checklist

Before merging, verify:

- [ ] No secrets or PHI leaked in the diff (gitleaks passed)
- [ ] Tests cover happy and sad paths
- [ ] Safety disclaimer and audit logging intact for sensitive actions
- [ ] Migration is reversible (if any)
- [ ] File size within maintainability budget
- [ ] Docs updated (design doc / ADR) if architecture changed
- [ ] Conventional Commit title on the PR

## Clinical Safety Gate

- [ ] No final diagnosis, treatment, prescription, or certainty-of-disease output introduced
- [ ] Output uses safe recommendation patterns only (see PRD Section 18)

## Merge Strategy

- **Squash merge** only. Keeps `main` linear; one PR = one commit on main.
- The squash commit message must be a valid Conventional Commit (release-please depends on it).

## Labels on PR

Apply at minimum: one `type/*`, one `area/*`, the current `sprint-N`, and a `size/*` label. Add `safety/phi` or `safety/clinical-review-needed` when relevant.

## CI Requirements

All required checks must pass before merge:
- secret-scan
- backend (lint, type, test)
- frontend (lint, type, test, build)

`docs-lint` is non-blocking (informational only).
