# Release Process

Releases are tagged per sprint using a modified SemVer scheme and automated with release-please.

## Versioning Scheme

Pre-1.0 prototype: `v0.<sprint>.<patch>`

| Tag | Meaning |
| --- | --- |
| v0.1.0 | End of Sprint 1 (Foundation) |
| v0.1.1 | Patch within Sprint 1 |
| v0.2.0 | End of Sprint 2 (Auth & Upload) |
| ... | ... |
| v0.8.0 | End of Sprint 8 (Demo-ready) |
| v1.0.0 | Skripsi defense baseline |
| v1.0.1+ | Post-defense maintenance |
| v1.1.0 | Sprint 9 (Phase 2 Prep) |

## Automated Flow (release-please)

1. Conventional Commits land on `main` via squash merges.
2. The release-please Action opens/updates a "release PR" that bumps the
   version and updates CHANGELOG.md from commit history.
3. Review the release PR. When ready, merge it.
4. release-please creates the git tag and a GitHub Release.

## Per-Sprint Manual Steps

After the automated release for a sprint:

1. Edit the GitHub Release:
   - Title: "Sprint N: <focus>" (e.g. "Sprint 1: Project Foundation")
   - Body: confirm auto-changelog, append acceptance criteria checklist.
2. Re-tag with sprint annotation if desired: `v0.1.0-sprint-1`.
3. Attach a PDF of release notes for the thesis appendix (optional).
4. Close the sprint milestone.
5. Open the next sprint milestone.

## Manual Tag (fallback)

If not using release-please for a given tag:

```bash
git switch main && git pull
git tag -a v0.1.0-sprint-1 -m "Sprint 1: Project Foundation"
git push origin v0.1.0-sprint-1
gh release create v0.1.0-sprint-1 --title "Sprint 1: Project Foundation" --notes-file release-notes.md
```

## Release Checklist

- [ ] All sprint acceptance criteria met
- [ ] CI green on main
- [ ] CHANGELOG updated (auto)
- [ ] Version bumped (auto)
- [ ] Tag annotated with sprint name
- [ ] GitHub Release published
- [ ] Milestone closed
- [ ] No critical safety/PHI debt carried over
