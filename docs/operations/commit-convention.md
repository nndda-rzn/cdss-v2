# Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for clear history and automated changelog generation via release-please.

## Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

## Types

| Type | Use for | Version bump |
| --- | --- | --- |
| feat | New feature | minor |
| fix | Bug fix | patch |
| docs | Documentation only | none |
| refactor | No behavior change | none |
| test | Tests | none |
| chore | Tooling, deps, maintenance | none |
| perf | Performance improvement | patch |
| security | PHI/auth/security change | patch |
| ci | CI/CD configuration | none |

`BREAKING CHANGE:` in footer triggers a major bump (post-1.0).

## Scopes

Project-specific scopes:

`auth`, `ecg`, `inference`, `hirescam`, `dt`, `audit`, `db`, `schema`, `ui`, `report`, `eval`, `infra`, `ci`, `deps`, `adr`

## Subject Rules

- Imperative mood ("add", not "added" or "adds").
- No trailing period.
- Lowercase start.
- Max ~72 chars.

## Body

- Explain the "why", not the "what" (the diff shows what).
- Wrap at ~72 chars.
- Reference issues: `Closes #12`, `Refs #34`.

## Examples

```
feat(auth): add JWT refresh token rotation with hash storage

Refresh tokens are now single-use. Each use issues a new refresh
token and stores its hash for revocation. Mitigates token replay
on unstable connections in remote facilities.

Closes #7
```

```
fix(inference): handle missing yolov11n-cls.pt gracefully

Return a structured INFERENCE_MODEL_NOT_FOUND error instead of
crashing when a model file is absent from models/.
```

```
docs(adr): record decision on petrol+charcoal color system
security(phi): enforce PHIAccessLog on Patient.name_encrypted decrypt
refactor(dt): extract DT-03 to dedicated rule file per granularity rule
chore(deps): upgrade pytorch 2.1->2.2 for cu121 compatibility
```

## Tooling

- `commitlint` validates messages via the `commit-msg` git hook (husky).
- `commitizen` (`cz commit` or `npm run commit`) provides an interactive prompt.
- release-please parses commits on `main` to generate CHANGELOG and version bumps.

## Setup

```bash
# In frontend/ (husky + commitlint live with the JS toolchain)
npm install
npx husky init
# commit-msg hook runs commitlint
```
