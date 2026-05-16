#!/usr/bin/env python3
"""Fail-closed checker for the Phase 13 Landlock syscall survey note."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_MARKERS = (
    "master-readback-2026-05-13",
    "planFopRulesetRelease()",
    "planRulesetFops()",
    "phase13-build-gate",
    "phase13_landlock_syscalls_reviewability.zig",
    "phase13_landlock_syscalls_manifest.json",
    "phase13_build.zig",
)

STALE_MARKERS = (
    "shared `phase13_build.zig` route still remains absent",
    "still-missing shared `zigux/tests/phase13_build.zig` route",
)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    survey_note = root / "Documentation" / "zigux" / "phase13-landlock-syscalls-survey.md"
    gap_note = root / "Documentation" / "zigux" / "phase13-landlock-syscalls-survey-gap.md"

    if not survey_note.is_file():
        issues.append(("MISSING_FILE", str(survey_note.relative_to(root))))
        return issues

    if not gap_note.is_file():
        issues.append(("MISSING_FILE", str(gap_note.relative_to(root))))

    text = survey_note.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(("MISSING_REQUIRED_MARKER", marker))

    for marker in STALE_MARKERS:
        if marker in text:
            issues.append(("STALE_SURVEY_MARKER", marker))

    return issues


def build_self_test_root(root: Path) -> None:
    (root / "Documentation" / "zigux").mkdir(parents=True, exist_ok=True)
    good_survey = """# Phase 13 Landlock Syscalls Survey

This bounded survey keeps the current helper packet honest.

- reviewed against live `master` `master-readback-2026-05-13`
- `planFopRulesetRelease()` stays explicit
- `planRulesetFops()` stays explicit
- `phase13-build-gate` stays explicit
- `phase13_landlock_syscalls_reviewability.zig` remains part of the packet
- `phase13_landlock_syscalls_manifest.json` remains part of the packet
- the shared `phase13_build.zig` route is present on current `master`
"""
    good_gap = """# Phase 13 Landlock Syscalls Survey Gap

Guard note for the stale survey wording.
"""
    (root / "Documentation" / "zigux" / "phase13-landlock-syscalls-survey.md").write_text(
        good_survey,
        encoding="utf-8",
    )
    (root / "Documentation" / "zigux" / "phase13-landlock-syscalls-survey-gap.md").write_text(
        good_gap,
        encoding="utf-8",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase13-landlock-survey-check-") as tmpdir:
        root = Path(tmpdir)
        build_self_test_root(root)

        assert collect_issues(root) == []
        checks_run += 1

        missing_marker = root / "Documentation" / "zigux" / "phase13-landlock-syscalls-survey.md"
        missing_marker.write_text(
            missing_marker.read_text(encoding="utf-8").replace("planRulesetFops()", "planRulesetWrapper()"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_REQUIRED_MARKER", "planRulesetFops()") in issues
        checks_run += 1

        build_self_test_root(root)
        stale_marker = root / "Documentation" / "zigux" / "phase13-landlock-syscalls-survey.md"
        stale_marker.write_text(
            stale_marker.read_text(encoding="utf-8")
            + "\nLegacy note: shared `phase13_build.zig` route still remains absent.\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "STALE_SURVEY_MARKER",
            "shared `phase13_build.zig` route still remains absent",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        shutil.rmtree(root / "Documentation" / "zigux")
        issues = collect_issues(root)
        assert ("MISSING_FILE", "Documentation/zigux/phase13-landlock-syscalls-survey.md") in issues
        checks_run += 1

    print("PHASE13_LANDLOCK_SYSCALLS_SURVEY_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE13_LANDLOCK_SYSCALLS_SURVEY_ALIGNMENT_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        for kind, detail in issues:
            print(f"{kind}:{detail}")
        return 1

    print("PHASE13_LANDLOCK_SYSCALLS_SURVEY_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
