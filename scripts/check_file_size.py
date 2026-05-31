#!/usr/bin/env python
"""File-size budget guard (pre-commit).

Keeps source files focused by failing the commit when a file exceeds its
line budget. Counts non-blank, non-comment lines so docstrings/blank spacing
don't penalise. Generated and test files are exempt.

Budgets (code lines, excluding blanks/comments):
  - Python modules (backend/app/**/*.py):    200
  - React components (frontend/src/**/*.tsx): 200
  - TS modules (frontend/src/**/*.ts):        200

Usage: python scripts/check_file_size.py [files...]
With no args, scans the tracked source tree (audit mode). In pre-commit,
lint-staged passes only the changed files, so the budget is enforced on
touch — pre-existing oversized files don't block unrelated commits.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EXEMPT_SUBSTRINGS = (
    "/migrations/",
    "/components/ui/",  # generated shadcn primitives
    "/.opencode/",
    "test_",
    ".test.",
    "/tests/",
)


def _budget(rel: str) -> int | None:
    rel = rel.replace("\\", "/")
    if any(s in f"/{rel}" for s in EXEMPT_SUBSTRINGS):
        return None
    if rel.startswith("backend/app/") and rel.endswith(".py"):
        return 200
    if rel.startswith("frontend/src/") and rel.endswith(".tsx"):
        return 200
    if rel.startswith("frontend/src/") and rel.endswith(".ts"):
        return 200
    return None


def _code_lines(path: Path) -> int:
    count = 0
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(("#", "//", "*", "/*")):
            continue
        count += 1
    return count


def _candidate_files(args: list[str]) -> list[Path]:
    if args:
        return [Path(a) for a in args]
    git = shutil.which("git") or "git"
    out = subprocess.run(  # noqa: S603
        [git, "ls-files", "backend/app", "frontend/src"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [REPO_ROOT / line for line in out.stdout.splitlines() if line]


def main(argv: list[str]) -> int:
    violations: list[str] = []
    for path in _candidate_files(argv):
        if not path.exists():
            continue
        try:
            rel = path.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = path.as_posix()
        budget = _budget(rel)
        if budget is None:
            continue
        lines = _code_lines(path)
        if lines > budget:
            violations.append(f"  {rel}: {lines} code lines (budget {budget})")

    if violations:
        print("File-size budget exceeded (split into focused modules):", file=sys.stderr)
        print("\n".join(violations), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))