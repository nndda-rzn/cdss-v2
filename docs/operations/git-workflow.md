# Git Workflow

Branching, naming, and lifecycle for EKG-Insight CDSS. Strategy: GitHub Flow + sprint tags.

## Branch Model

```
main (protected, always deployable)
 ├── feat/sprint-1/auth-jwt
 ├── fix/migration-rollback
 ├── docs/sprint-2-design
 ├── refactor/services/decision-tree-extraction
 ├── security/phi-access-log
 └── chore/deps/pytorch-upgrade
```

- `main` is the single source of truth and is protected.
- Branch from `main`, open a PR, merge back, delete the branch.
- Sprint scope is tracked via labels and milestones, not long-lived branches.
- Releases are tagged per sprint.

## Branch Naming

Format: `<type>/<sprint-or-area>/<short-kebab>`

| Type | Purpose |
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

Rules: kebab-case, max 50 chars, 3 segments ideal.

Examples:
- `feat/sprint-1/encryption-bootstrap`
- `fix/inference/missing-model-file`
- `security/phi-access-log`
- `docs/adr-0010-color-system`

## Lifecycle

```
1. git switch main && git pull
2. git switch -c feat/sprint-1/auth-jwt
3. (work, commit using Conventional Commits)
4. git push -u origin feat/sprint-1/auth-jwt
5. Open PR -> CI runs -> self-review (cooldown for size/m+)
6. Squash merge to main
7. Delete branch (local + remote)
```

## Why Not Alternatives

| Alternative | Why not |
| --- | --- |
| GitFlow (main+develop) | Two long-lived branches = noise for solo dev |
| Pure trunk-based | Loses PR self-review opportunity |
| Sprint long-branch | Merge conflict risk between sprints |

## Tags & Releases

- Tag at end of each sprint: `v0.1.0-sprint-1`, `v0.2.0-sprint-2`, etc.
- Tags are annotated; sign with GPG if available.
- See [release-process.md](release-process.md) for the full flow.

## History Hygiene

- Squash merge keeps `main` history linear and readable.
- Never force-push to `main`.
- Never rewrite published history.
- Keep commits scoped; one logical change per commit.
