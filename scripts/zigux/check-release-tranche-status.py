#!/usr/bin/env python3
"""Fail-closed checker for the PMO release tranche status note."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/release-tranche-status.md")

REQUIRED_MARKERS = (
    "# Zigux Release Tranche Status",
    "`RELEASE_STATUS=active`",
    "`RELEASE_CLOSURE_COMPLETE=no`",
    "commit-train entries `15. docs(zigux): close bounded phase-1 helper tranche` and `22. docs(zigux): close bounded Phase 2 toolchain tranche`",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase1-closure.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "historical tranche targets that need re-materialization",
    "starting with `Documentation/zigux/README.md`",
)

FORBIDDEN_MARKERS = (
    "`RELEASE_CLOSURE_COMPLETE=yes`",
    "Phase 1 is directly readable on current `master`",
    "Phase 2 is directly readable on current `master`",
)


def validate_note(text: str) -> list[str]:
    problems: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            problems.append(f"missing required marker: {marker}")

    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            problems.append(f"forbidden marker present: {marker}")

    return problems


def run_self_test() -> int:
    sample = "\n".join(REQUIRED_MARKERS)
    if validate_note(sample):
        print("self-test failed: valid sample should pass", file=sys.stderr)
        return 1

    broken = sample.replace("`RELEASE_CLOSURE_COMPLETE=no`", "`RELEASE_CLOSURE_COMPLETE=yes`")
    problems = validate_note(broken)
    if not problems:
        print("self-test failed: broken sample should fail", file=sys.stderr)
        return 1

    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    note_path = args.repo_root / NOTE_PATH
    if not note_path.is_file():
        print(f"missing note: {note_path}", file=sys.stderr)
        return 1

    problems = validate_note(note_path.read_text(encoding="utf-8"))
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1

    print(f"ok: {NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())