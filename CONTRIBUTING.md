# Contributing to EKG-Insight CDSS

Thank you for contributing. This guide covers development setup, branching, commits, and the pull request flow. This is a research project targeting publication; documentation discipline matters.

## Prerequisites

- Python 3.11
- Node.js 20 LTS
- Git
- (Optional) `gh` CLI for GitHub operations

## Development Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Unix
pip install -e ".[dev]"
python ../scripts/init_secrets.py
alembic upgrade head
python ../scripts/seed_facility.py
python ../scripts/seed_admin.py
flask run                     # http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173 (proxies /api to :5000)
```

## Branch Strategy (GitHub Flow + Sprint Tags)

- `main` is protected and always deployable.
- Create a branch from `main`, open a PR, merge back, delete branch.
- Sprint scope is tracked via labels and milestones, not long-lived branches.
- Releases are tagged per sprint: `v0.1.0-sprint-1`, `v0.2.0-sprint-2`, etc.

### Branch Naming

Format: `<type>/<sprint-or-area>/<short-kebab>`

| Type | For |
| --- | --- |
| feat/ | New feature |
| fix/ | Bug fix |
| docs/ | Documentation |
| refactor/ | No behavior change |
| test/ | Tests |
| chore/ | Tooling, deps |
| perf/ | Performance |
| security/ | PHI/auth-related (extra review) |
| exp/ | Research experiment |

Example: `feat/sprint-1/auth-jwt`, `security/phi-access-log`.

## Commit Convention (Conventional Commits)

Format: `<type>(<scope>): <subject>`

Scopes: auth, ecg, inference, hirescam, dt, audit, db, schema, ui, report, eval, infra, ci, deps.

Examples:

```
feat(auth): add JWT refresh token rotation with hash storage
fix(inference): handle missing yolov11n-cls.pt gracefully
docs(adr): record decision on petrol+charcoal color system
security(phi): enforce PHIAccessLog on Patient.name_encrypted decrypt
```

- Body explains "why", not "what".
- Reference issues: `Closes #12`.
- Breaking changes: `BREAKING CHANGE:` footer.

`commitlint` validates messages via the commit-msg hook.

## Pull Request Flow

1. Branch from `main`.
2. Make conventional commits.
3. Push and open a PR (template loads automatically).
4. CI runs: lint, type-check, test, build, secret scan.
5. Self-review after a cooldown (24h for size/m+ changes).
6. Address your own review comments.
7. Squash merge to `main`; delete branch.

### Self-Review Checklist

- [ ] No secrets or PHI leaked in the diff
- [ ] Tests cover happy and sad paths
- [ ] Safety disclaimer and audit logging intact for sensitive actions
- [ ] Migration is reversible (if any)
- [ ] File size within maintainability budget (see architecture doc)

## Code Quality

| Area | Tools |
| --- | --- |
| Python | ruff (lint), mypy (types), pytest (tests) |
| TypeScript | eslint, prettier, tsc, vitest |
| Commits | commitlint |
| Secrets | gitleaks |

Run locally before pushing:

```bash
# Backend
cd backend && ruff check . && mypy . && pytest
# Frontend
cd frontend && npm run lint && npm run typecheck && npm run test
```

## Maintainability Rules

- One file = one concept. Respect the line budget (see architecture-overview-design.md).
- Page/orchestrator files are composition only.
- Wrap reusable library usage in dedicated files.

## Documentation

- Significant architectural choices get an ADR in `docs/adr/`.
- Each sprint has a design doc in `docs/superpowers/specs/`.
- Update relevant docs in the same PR as the code change.

## Clinical Safety

Never introduce output that gives final diagnosis, treatment, prescription, or certainty of disease. See [SECURITY.md](SECURITY.md) and PRD Section 18.
