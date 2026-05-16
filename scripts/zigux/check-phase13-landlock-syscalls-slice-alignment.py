#!/usr/bin/env python3
"""Fail-closed checker for the Phase 13 Landlock syscall slice note."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_MARKERS = (
    "fop_ruleset_release()",
    "ruleset_fops",
    "phase13_landlock_syscalls_reviewability.zig",
    "phase13_build.zig",
)

STALE_MARKERS = (
    "get_ruleset_from_fd()",
    "get_path_from_fd()",
    "add_rule_path_beneath()",
)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    slice_note = root / "Documentation" / "zigux" / "phase13-landlock-syscalls-slice.md"
    gap_note = root / "Documentation" / "zigux" / "phase13-landlock-syscalls-slice-gap.md"

    if not slice_note.is_file():
        issues.append(("MISSING_FILE", str(slice_note.relative_to(root))))
        return issues

    if not gap_note.is_file():
        issues.append(("MISSING_FILE", str(gap_note.relative_to(root))))

    text = slice_note.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(("MISSING_REQUIRED_MARKER", marker))

    for marker in STALE_MARKERS:
        if marker in text:
            issues.append(("STALE_SLICE_MARKER", marker))

    return issues


def build_self_test_root(root: Path) -> None:
    (root / "Documentation" / "zigux").mkdir(parents=True, exist_ok=True)
    good_slice = """# Phase 13 Landlock Syscalls Slice

This bounded Phase 13 slice keeps the current helper packet honest.

- `fop_ruleset_release()` stays explicit
- `ruleset_fops` stays explicit
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig` remains part of the review packet
- the missing shared `phase13_build.zig` route stays explicit
"""
    good_gap = """# Phase 13 Landlock Syscalls Slice Gap

Guard note for the stale slice wording.
"""
    (root / "Documentation" / "zigux" / "phase13-landlock-syscalls-slice.md").write_text(
        good_slice,
        encoding="utf-8",
    )
    (root / "Documentation" / "zigux" / "phase13-landlock-syscalls-slice-gap.md").write_text(
        good_gap,
        encoding="utf-8",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase13-landlock-slice-check-") as tmpdir:
        root = Path(tmpdir)
        build_self_test_root(root)

        assert collect_issues(root) == []
        checks_run += 1

        missing_marker = root / "Documentation" / "zigux" / "phase13-landlock-syscalls-slice.md"
        missing_marker.write_text(
            missing_marker.read_text(encoding="utf-8").replace("ruleset_fops", "ruleset wrapper"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_REQUIRED_MARKER", "ruleset_fops") in issues
        checks_run += 1

        build_self_test_root(root)
        stale_marker = root / "Documentation" / "zigux" / "phase13-landlock-syscalls-slice.md"
        stale_marker.write_text(
            stale_marker.read_text(encoding="utf-8") + "\nLegacy next step: add_rule_path_beneath().\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("STALE_SLICE_MARKER", "add_rule_path_beneath()") in issues
        checks_run += 1

        build_self_test_root(root)
        shutil.rmtree(root / "Documentation" / "zigux")
        issues = collect_issues(root)
        assert ("MISSING_FILE", "Documentation/zigux/phase13-landlock-syscalls-slice.md") in issues
        checks_run += 1

    print("PHASE13_LANDLOCK_SYSCALLS_SLICE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE13_LANDLOCK_SYSCALLS_SLICE_ALIGNMENT_SELF_TEST_CASES={checks_run}")
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

    print("PHASE13_LANDLOCK_SYSCALLS_SLICE_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
