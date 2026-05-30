# Repository Setup

First-time setup checklist for pushing EKG-Insight CDSS to GitHub (private).

## Prerequisites

- `git` installed
- `gh` CLI installed and authenticated (`gh auth login`)
- This documentation baseline committed locally

## 1. Initialize Git

```bash
git init
git branch -M main
```

## 2. Verify .gitignore Works (CRITICAL)

```bash
git add .gitignore .gitattributes .editorconfig
git commit -m "chore: initial gitignore and editor config"
git add .
git status
```

Confirm the following are NOT staged:
- `secrets/`
- `data/`, `*.db`
- `storage/`
- `models/**/*.pt`
- `.env`

If any appear, fix `.gitignore` before committing.

## 3. Initial Commit

```bash
git commit -m "docs: initial documentation baseline (sprint 0)"
```

## 4. Create Private Repo

```bash
gh repo create CDSS-web-project-v2 \
  --private \
  --source=. \
  --remote=origin \
  --description "Interpretable CDSS for ECG-based MI screening in low-resource primary healthcare (research prototype)"
git push -u origin main
```

## 5. Update Placeholders

- In `.github/CODEOWNERS`: replace `@maintainer` with your GitHub username.
- In `CITATION.cff`: fill author name, affiliation, ORCID, repository-code URL.
- In `.github/ISSUE_TEMPLATE/config.yml`: fix the SECURITY.md contact URL.

## 6. Create Labels

```bash
# Requires a label sync tool, or create manually. Example with gh:
gh label create "type/feat" --color "0E8A16" --description "New feature"
# ... (see .github/labels.yml for the full list)
```

Or use a labeler action / `gh-label` extension to bulk import `.github/labels.yml`.

## 7. Create Milestones

```bash
for i in 1 2 3 4 5 6 7 8 9; do
  gh api repos/:owner/:repo/milestones -f title="Sprint $i" -f state=open
done
```

## 8. Apply Branch Protection

Let CI run once (push triggers it), then follow [branch-protection.md](branch-protection.md).

## 9. Configure Merge Settings

```bash
gh repo edit --enable-squash-merge --delete-branch-on-merge
```

## 10. Create Project Board (optional)

Create a board with columns: Backlog, Design, Ready, In Progress, In Review, Done. Add a per-sprint filter view.

## 11. Enable Dependabot & Code Scanning

Dependabot is configured via `.github/dependabot.yml` (auto-active on push). Enable secret scanning in repo Settings > Code security.

## Post-Setup Verification

- [ ] Repo is private
- [ ] No secrets/PHI in history (`git log --stat`)
- [ ] CI runs on first push
- [ ] Labels created
- [ ] Milestones created
- [ ] Branch protection applied
- [ ] CODEOWNERS and CITATION placeholders filled
