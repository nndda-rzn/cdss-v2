# Branch Protection

Settings to apply manually (or via `gh` CLI) on the `main` branch after repository creation.

## Required Settings

| Setting | Value |
| --- | --- |
| Require a pull request before merging | Enabled |
| Required approvals | 0 (solo; CODEOWNERS = self) |
| Dismiss stale approvals | Enabled |
| Require status checks to pass | Enabled |
| Required checks | secret-scan, backend, frontend |
| Require branches up to date before merge | Enabled |
| Require conversation resolution | Enabled |
| Require linear history | Enabled |
| Allow force pushes | Disabled |
| Allow deletions | Disabled |
| Include administrators | Enabled (apply to self for discipline) |
| Require signed commits | Optional (if GPG configured) |

## Apply via gh CLI

```bash
gh api -X PUT repos/:owner/:repo/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f "required_status_checks[strict]=true" \
  -f "required_status_checks[checks][][context]=secret-scan" \
  -f "required_status_checks[checks][][context]=backend" \
  -f "required_status_checks[checks][][context]=frontend" \
  -f "enforce_admins=true" \
  -f "required_pull_request_reviews[required_approving_review_count]=0" \
  -f "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  -f "required_linear_history=true" \
  -f "allow_force_pushes=false" \
  -f "allow_deletions=false" \
  -f "required_conversation_resolution=true" \
  -f "restrictions=null"
```

Note: status check contexts must exist (at least one CI run) before they can be marked required. Push an initial commit, let CI run once, then apply protection.

## Merge Settings (repo-level)

| Setting | Value |
| --- | --- |
| Allow merge commits | Disabled |
| Allow squash merging | Enabled (default) |
| Allow rebase merging | Disabled |
| Auto-delete head branches | Enabled |

```bash
gh repo edit --enable-squash-merge --enable-merge-commit=false \
  --enable-rebase-merge=false --delete-branch-on-merge
```
